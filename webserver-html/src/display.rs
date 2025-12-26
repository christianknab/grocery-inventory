use defmt::info;
use heapless::String;
use picoserve::response::IntoResponse;
use crate::GlobalAppState;

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

    let mut display = state.display.lock().await;
    display.clear();
    let success = display.draw_image(&input.0.header, &input.0.body).is_ok();

    picoserve::response::Json(DisplayResponse { success })
}
