use embedded_graphics::{
    mono_font::{MonoTextStyle, ascii::FONT_6X10},
    pixelcolor::BinaryColor,
    prelude::*,
    primitives::{PrimitiveStyle, Rectangle},
    text::{Alignment, Text},
};
use embedded_hal::i2c::I2c;
use heapless::String;
use ssd1306::{I2CDisplayInterface, Ssd1306, mode::BufferedGraphicsMode, prelude::*};
use display_interface::DisplayError;
use embassy_time::{Duration, Instant};

pub struct DisplayController<I2C> {
    display: Ssd1306<I2CInterface<I2C>, DisplaySize128x64, BufferedGraphicsMode<DisplaySize128x64>>,
    header: String<64>,
    body: String<256>,
    last_draw: Option<Instant>,
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
            last_draw: None,
        })
    }

    pub fn clear(&mut self) -> Result<(), DisplayError> {
        self.display.clear(BinaryColor::Off)?;
        let r = self.display.flush();
        if r.is_ok() {
            self.last_draw = None;
        }
        r
    }

    pub fn clear_if_idle(&mut self, timeout: Duration) -> Result<bool, DisplayError> {
        let Some(t) = self.last_draw else {
            return Ok(false);
        };
        if Instant::now().saturating_duration_since(t) < timeout {
            return Ok(false);
        }
        self.clear()?;
        Ok(true)
    }

    fn draw_wrapped_body(
        &mut self,
        body: &str,
        top_left: Point,
        max_width_px: i32,
        max_height_px: i32,
        text_style: MonoTextStyle<'_, BinaryColor>,
    ) {
        // FONT_6X10 dim
        let char_w: i32 = 6;
        let line_h: i32 = 10;

        let max_cols: usize = (max_width_px.max(0) / char_w) as usize;
        let max_lines: usize = (max_height_px.max(0) / line_h) as usize;
        if max_cols == 0 || max_lines == 0 {
            return;
        }

        let mut y = top_left.y;
        let mut line: String<64> = String::new();
        let mut lines_used: usize = 0;

        let draw_line = |this: &mut Self, s: &str, y: i32| {
            Text::new(s, Point::new(top_left.x, y), text_style)
                .draw(&mut this.display)
                .ok();
        };

        let commit_line = |this: &mut Self, line: &mut String<64>, y: &mut i32, lines_used: &mut usize, allow_empty: bool| -> bool {
            if !line.is_empty() {
                draw_line(this, line.as_str(), *y);
                line.clear();
            } else if !allow_empty {
                return true;
            }
            if *lines_used >= max_lines {
                return false;
            }
            *y += line_h;
            *lines_used += 1;
            true
        };

        let mut paragraphs = body.split('\n').peekable();
        while let Some(raw) = paragraphs.next() {
            let raw = raw.trim_end_matches('\r');

            for word in raw.split_whitespace() {
                // Hard wrap too long words
                let mut w = word;
                while w.len() > max_cols {
                    if lines_used >= max_lines {
                        return;
                    }
                    let (head, tail) = w.split_at(max_cols);
                    draw_line(self, head, y);
                    y += line_h;
                    lines_used += 1;
                    w = tail;
                }

                let add_len = if line.is_empty() { w.len() } else { 1 + w.len() };
                if line.len() + add_len > max_cols {
                    if !commit_line(self, &mut line, &mut y, &mut lines_used, false) {
                        return;
                    }
                }

                if !line.is_empty() {
                    let _ = line.push(' ');
                }
                let _ = line.push_str(w);
            }

            // Explicit newline: flush current line (if any) and advance one line,
            // even if the line is empty
            if paragraphs.peek().is_some() {
                if !commit_line(self, &mut line, &mut y, &mut lines_used, true) {
                    return;
                }
            }
        }

        // Flush last line without forcing another newline advance.
        if !line.is_empty() && lines_used < max_lines {
            draw_line(self, &line, y);
        }
    }

    pub fn draw_image(&mut self, header: &str, body: &str) -> Result<(), DisplayError> {
        self.header.clear();
        self.body.clear();
        let _ = self.header.push_str(header);
        let _ = self.body.push_str(body);

        self.display.clear(BinaryColor::Off)?;

        // Draw header background
        Rectangle::new(Point::new(0, 0), Size::new(128, 12))
            .into_styled(PrimitiveStyle::with_fill(BinaryColor::On))
            .draw(&mut self.display)
            .ok();

        // Draw header text
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
        self.draw_wrapped_body(
            body,
            Point::new(0, 24),
            128,         // full screen width
            64 - 24,    // remaining height under header
            text_style,
        );

        let r = self.display.flush();
        if r.is_ok() {
            self.last_draw = Some(Instant::now());
        }
        r
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
