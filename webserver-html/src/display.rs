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
pub struct UiRequest {
    /// Header text
    header: Option<String<64>>,
    /// Body text
    body: Option<String<256>>,
    /// LED color selector: "red" | "green" | "".
    color: Option<String<16>>,
}

#[derive(serde::Serialize)]
pub struct UiResponse {
    success: bool,
}

pub async fn ui_handler(
    picoserve::extract::State(state): picoserve::extract::State<&'static GlobalAppState>,
    input: picoserve::extract::Json<UiRequest>,
) -> impl IntoResponse {
    let mut updated_anything = false;

    if input.0.header.is_none() && input.0.body.is_none() && input.0.color.is_none() {
        return picoserve::response::Json(UiResponse { success: false });
    }

    if let Some(ref header) = input.0.header {
        info!("Header: {}", header);
    }
    if let Some(ref body) = input.0.body {
        info!("Body: {}", body);
    }
    if let Some(ref color) = input.0.color {
        info!("Color: {}", color);
    }

    // Validate `color` first; if invalid, do not update anything.
    if let Some(ref color) = input.0.color {
        let mut leds = state.leds.lock().await;
        if !leds.update_from_color(color.as_str()) {
            return picoserve::response::Json(UiResponse { success: false });
        }
        updated_anything = true;
    }

    if input.0.header.is_some() || input.0.body.is_some() {
        let mut display = state.display.lock().await;

        match (&input.0.header, &input.0.body) {
            (Some(header), Some(body)) => {
                updated_anything = display.draw_image(header.as_str(), body.as_str()).is_ok();
            }
            (Some(header), None) => {
                display.set_header(header.as_str());
                updated_anything = display.refresh().is_ok() || updated_anything;
            }
            (None, Some(body)) => {
                display.set_body(body.as_str());
                updated_anything = display.refresh().is_ok() || updated_anything;
            }
            (None, None) => {}
        }
    }

    picoserve::response::Json(UiResponse {
        success: updated_anything,
    })
}
