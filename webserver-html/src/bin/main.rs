#![no_std]
#![no_main]
#![deny(
    clippy::mem_forget,
    reason = "mem::forget is generally not safe to do with esp_hal types, especially those \
    holding buffers for the duration of a data transfer."
)]
#![deny(clippy::large_stack_frames)]

use defmt::info;
use embassy_executor::Spawner;
use embassy_time::{Duration, Timer};
use esp_hal::clock::CpuClock;
use esp_hal::rng::Rng;
use esp_hal::timer::timg::TimerGroup;
use esp_println as _;

#[panic_handler]
fn panic(_: &core::panic::PanicInfo) -> ! {
    loop {}
}

extern crate alloc;

use alloc::format;

// This creates a default app-descriptor required by the esp-idf bootloader.
// For more information see: <https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/system/app_image_format.html#application-description>
esp_bootloader_esp_idf::esp_app_desc!();

#[allow(
    clippy::large_stack_frames,
    reason = "it's not unusual to allocate larger buffers etc. in main"
)]

use webserver_html as lib;
use lib::display_controller::DisplayController;
use lib::display::display_idle_clear_task;
use lib::led_controller::LedController;
use esp_hal::gpio::Pin;

#[esp_rtos::main]
async fn main(spawner: Spawner) -> ! {
    // generator version: 1.1.0

    let config = esp_hal::Config::default().with_cpu_clock(CpuClock::max());
    let peripherals = esp_hal::init(config);

    esp_alloc::heap_allocator!(#[esp_hal::ram(reclaimed)] size: 66320);

    let timg0 = TimerGroup::new(peripherals.TIMG0);
    let sw_interrupt =
        esp_hal::interrupt::software::SoftwareInterruptControl::new(peripherals.SW_INTERRUPT);
    esp_rtos::start(timg0.timer0, sw_interrupt.software_interrupt0);

    info!("Embassy initialized!");

    // Initialize I2C for display
    let i2c0 = esp_hal::i2c::master::I2c::new(
        peripherals.I2C0,
        esp_hal::i2c::master::Config::default().with_frequency(esp_hal::time::Rate::from_khz(400))
        // esp_hal::i2c::master::Config {
        //     frequency: 400.kHz(),
        //     timeout: Some(1000),
        // },
    )
    .expect("Failed to init I2C0") // <-- unwrap Result<I2c<...>, ConfigError>
    .with_sda(peripherals.GPIO10)
    .with_scl(peripherals.GPIO8)
    .into_async();

    // Initialize display controller
    let mut display_controller = DisplayController::new(i2c0)
        .expect("Failed to initialize display");

    // Initialize LED controller (GPIO7 = ADDING, GPIO6 = REMOVING)
    let led_controller = LedController::new(peripherals.GPIO5.degrade(), peripherals.GPIO4.degrade());

    let app_state = lib::mk_static!(
        lib::GlobalAppState,
        lib::AppState::new(display_controller, led_controller)
    );

    let mut display = app_state.display.lock().await;

    display.draw_image("SETTING UP", "Initializing WIFI...").expect("display err");
    
    let radio_init = &*lib::mk_static!(
        esp_radio::Controller<'static>,
        esp_radio::init().expect("Failed to initialize Wi-Fi/BLE controller")
    );
    let rng = Rng::new();

    let (stack, ip) = lib::wifi::start_wifi(radio_init, peripherals.WIFI, rng, &spawner).await;

    let line2 = format!("IP: {}", ip);
    display
        .draw_image("SUCCESS!", &line2)
        .expect("display err");

    drop(display);

    spawner.must_spawn(display_idle_clear_task(app_state));

    let web_app = lib::web::WebApp::new(app_state);
    for id in 0..lib::web::WEB_TASK_POOL_SIZE {
        spawner.must_spawn(lib::web::web_task(
            id,
            stack,
            web_app.router,
            web_app.config,
        ));
    }

    loop {
        Timer::after(Duration::from_secs(1)).await;
    }
}
