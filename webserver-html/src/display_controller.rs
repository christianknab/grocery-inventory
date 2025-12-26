use embedded_graphics::{
    mono_font::{ascii::FONT_6X10, MonoTextStyle},
    pixelcolor::BinaryColor,
    prelude::*,
    primitives::{PrimitiveStyle, Rectangle},
    text::{Alignment, Text},
};
use embedded_hal::i2c::I2c;
use heapless::String;
use ssd1306::{I2CDisplayInterface, Ssd1306, mode::BufferedGraphicsMode, prelude::*};
use display_interface::DisplayError;

pub struct DisplayController<I2C> {
    display: Ssd1306<I2CInterface<I2C>, DisplaySize128x64, BufferedGraphicsMode<DisplaySize128x64>>,
    header: String<64>,
    body: String<256>,
}

impl<I2C> DisplayController<I2C>
where
    I2C: I2c,
{
    pub fn new(i2c: I2C) -> Result<Self, DisplayError> {
        let interface = I2CDisplayInterface::new(i2c);
        let mut display = Ssd1306::new(interface, DisplaySize128x64, DisplayRotation::Rotate0)
            .into_buffered_graphics_mode();
        
        display.init()?;
        display.clear(BinaryColor::Off)?;
        display.clear_buffer();
        display.flush()?;

        Ok(Self {
            display,
            header: String::new(),
            body: String::new(),
        })
    }

    pub fn clear(&mut self) -> Result<(), DisplayError> {
        self.display.clear(BinaryColor::Off)?;
        self.display.clear_buffer();
        self.display.flush()
    }

    pub fn draw_image(&mut self, header: &str, body: &str) -> Result<(), DisplayError> {
        // self.header.clear();
        // self.body.clear();
        // let _ = self.header.push_str(header);
        // let _ = self.body.push_str(body);

        self.display.clear(BinaryColor::Off)?;
        self.display.clear_buffer();

        // Draw header background (filled rectangle)
        Rectangle::new(Point::new(0, 0), Size::new(128, 120))
            .into_styled(PrimitiveStyle::with_fill(BinaryColor::On))
            .draw(&mut self.display)
            .ok();

        // Draw header text (inverted color)
        let text_style = MonoTextStyle::new(&FONT_6X10, BinaryColor::Off);
        Text::with_alignment(
            header,
            Point::new(64, 8),
            text_style,
            Alignment::Center,
        )
        .draw(&mut self.display)
        .ok();

        // Draw body text
        let text_style = MonoTextStyle::new(&FONT_6X10, BinaryColor::On);
        Text::new(body, Point::new(0, 24), text_style)
            .draw(&mut self.display)
            .ok();

        self.display.flush()
    }

    pub fn set_header(&mut self, header: &str) {
        self.header.clear();
        let _ = self.header.push_str(header);
    }

    pub fn set_body(&mut self, body: &str) {
        self.body.clear();
        let _ = self.body.push_str(body);
    }

    pub fn refresh(&mut self) -> Result<(), DisplayError> {
        self.draw_image(&self.header.clone(), &self.body.clone())
    }
}
