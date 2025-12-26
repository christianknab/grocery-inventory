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
}
