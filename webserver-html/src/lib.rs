#![no_std]
#![feature(impl_trait_in_assoc_type)]

pub mod display;
pub mod display_controller;
pub mod web;
pub mod wifi;

use embassy_sync::blocking_mutex::raw::CriticalSectionRawMutex;
use embassy_sync::mutex::Mutex;

pub struct AppState<I2C> {
    pub display: Mutex<CriticalSectionRawMutex, display_controller::DisplayController<I2C>>,
}

impl<I2C> AppState<I2C> {
    pub fn new(display: display_controller::DisplayController<I2C>) -> Self {
        Self {
            display: Mutex::new(display),
        }
    }
}

/// Concrete I2C type used by the SSD1306 display in this firmware.
///
/// NOTE: `esp_hal::i2c::master::I2c` is generic only over the data-mode (`Dm`)
/// (plus the lifetime), not over the peripheral type.
pub type DisplayI2c = esp_hal::i2c::master::I2c<'static, esp_hal::Async>;

/// Single concrete app-state type shared by the web server + handlers.
pub type GlobalAppState = AppState<DisplayI2c>;

#[macro_export]
macro_rules! mk_static {
    ($t:ty,$val:expr) => {{
        static STATIC_CELL: static_cell::StaticCell<$t> = static_cell::StaticCell::new();
        #[deny(unused_attributes)]
        let x = STATIC_CELL.uninit().write(($val));
        x
    }};
}
