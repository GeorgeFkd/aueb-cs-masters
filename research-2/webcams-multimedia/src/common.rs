pub mod common {
    use gst::prelude::*;
    use gstreamer::{
        self as gst,
        ffi::{gst_element_factory_make, GstCaps, GstElement, GstElementFactory},
        glib, Caps,
    }; //based on some param i can give different results for these two,
       //mb env variables
    pub fn encoding_tuple() -> (gst::Element, gst::Element) {
        let deadline: i64 = 1;
        let video_encoder = gst::ElementFactory::make("vp8enc")
            .name("encoder")
            .property("deadline", deadline)
            .build()
            .expect("vp8enc could not be made");

        let rtppay = gst::ElementFactory::make("rtpvp8pay")
            .name("rtp-vp8-pay")
            .build()
            .expect("rtpvp8pay could not be made");

        (video_encoder, rtppay)
    }

    pub fn decoding_tuple() -> (gst::Element, gst::Element) {
        let rtpdepay = gst::ElementFactory::make("rtpvp8depay")
            .name("depayer")
            .build()
            .expect("rtpvp8depay could not be made");

        let video_decoder = gst::ElementFactory::make("vp8dec")
            .name("decoder")
            .build()
            .expect("vp8dec could not be made");
        (video_decoder, rtpdepay)
    }
}
