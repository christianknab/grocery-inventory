use defmt::info;
use heapless::String;
use picoserve::response::IntoResponse;
use crate::GlobalAppState;
use embassy_time::{Duration, Timer};

pub const DISPLAY_IDLE_TIMEOUT: Duration = Duration::from_secs(2*60);

#[embassy_executor::task]
pub async fn display_idle_clear_task(state: &'static GlobalAppState) -> ! {
    loop {
        Timer::after(Duration::from_secs(5)).await; // poll interval
        let mut display = state.display.lock().await;
        if let Ok(true) = display.clear_if_idle(DISPLAY_IDLE_TIMEOUT) {
            drop(display);
            let mut leds = state.leds.lock().await;
            leds.off();
        }
    }
}

#[derive(serde::Deserialize)]
pub struct DisplayRequest {
    header: String<64>,
    body: String<256>,
}

#[derive(serde::Serialize)]
pub struct DisplayResponse {
    success: bool,
}

pub async fn display_handler(
    picoserve::extract::State(state): picoserve::extract::State<&'static GlobalAppState>,
    input: picoserve::extract::Json<DisplayRequest>,
) -> impl IntoResponse {
    info!("Header: {}", input.0.header);
    info!("Body: {}", input.0.body);

    {
        let mut leds = state.leds.lock().await;
        leds.update_from_header(&input.0.header);
    }

    let mut display = state.display.lock().await;
    display.clear();
    let success = display.draw_image(&input.0.header, &input.0.body).is_ok();

    picoserve::response::Json(DisplayResponse { success })
}
