use esp_hal::gpio::{AnyPin, Level, Output, OutputConfig};

pub struct LedController<'a> {
    adding: Output<'a>,   // GPIO7
    removing: Output<'a>, // GPIO6
}

impl<'a> LedController<'a> {
    pub fn new(adding_pin: AnyPin<'a>, removing_pin: AnyPin<'a>) -> Self {
        let adding = Output::new(adding_pin, Level::Low, OutputConfig::default());
        let removing = Output::new(removing_pin, Level::Low, OutputConfig::default());
        Self { adding, removing }
    }

    pub fn off(&mut self) {
        self.adding.set_low();
        self.removing.set_low();
    }

    pub fn set_adding(&mut self) {
        self.adding.set_high();
        self.removing.set_low();
    }

    pub fn set_removing(&mut self) {
        self.adding.set_low();
        self.removing.set_high();
    }

    pub fn update_from_header(&mut self, header: &str) {
        match header.trim() {
            "ADDING" => self.set_adding(),
            "REMOVING" => self.set_removing(),
            _ => self.off(),
        }
    }

    /// Updates LEDs from a color string.
    ///
    /// - "green" => `set_adding()`
    /// - "red" => `set_removing()`
    /// - "" => `off()`
    /// - anything else => no change
    ///
    /// Returns `true` if the input was recognized (including empty string).
    pub fn update_from_color(&mut self, color: &str) -> bool {
        let color = color.trim();
        if color.is_empty() {
            self.off();
            return true;
        }

        match color {
            "green" | "GREEN" | "Green" => {
                self.set_adding();
                true
            }
            "red" | "RED" | "Red" => {
                self.set_removing();
                true
            }
            _ => false,
        }
    }
}
