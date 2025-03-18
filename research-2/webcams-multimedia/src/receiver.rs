mod common;

use std::{process::Command, str::FromStr};

use gst::prelude::*;
use gstreamer::{
    self as gst,
    ffi::{gst_element_factory_make, GstCaps, GstElement, GstElementFactory},
    glib, Caps,
};
fn main() {
    gst::init().unwrap();
    let video_output = gst::ElementFactory::make("autovideosink")
        .name("sink")
        .build()
        .expect("Could not create GST Element");
    let port: i32 = 2001;
    let udp_source = gst::ElementFactory::make("udpsrc")
        .name("network-receive")
        .property("port", port)
        .build()
        .expect("udpsink could not be made");
    let capsfilter = gst::ElementFactory::make("capsfilter")
        .name("capper")
        .build()
        .expect("capsfilter could not be made");
    let rtp_jitter_buffer = gst::ElementFactory::make("rtpjitterbuffer")
        .name("rtp-jitter-buffer")
        .build()
        .expect("rtpjitterbuffer could not be made");

    let video_convert = gst::ElementFactory::make("videoconvert")
        .name("converter")
        .build()
        .expect("videoconvert could not be made");

    let pipeline = gst::Pipeline::with_name("Video Receiver");
    let caps =
        Caps::from_str("application/x-rtp,media=video,encoding-name=VP8,payload=96").unwrap();
    capsfilter.set_property("caps", &caps);
    let (video_decoder, rtpdepay) = common::common::decoding_tuple();
    pipeline
        .add_many([
            &udp_source,
            &capsfilter,
            &rtp_jitter_buffer,
            &rtpdepay,
            &video_decoder,
            &video_convert,
            &video_output,
        ])
        .unwrap();

    gst::Element::link_many([
        &udp_source,
        &capsfilter,
        &rtp_jitter_buffer,
        &rtpdepay,
        &video_decoder,
        &video_convert,
        &video_output,
    ])
    .expect("Linking elements was not successfull");
    pipeline
        .set_state(gst::State::Playing)
        .expect("Unable to set the pipeline to the `Playing` state");
    pipeline.set_latency(gst::ClockTime::from_mseconds(50));
    let bus = pipeline.bus().expect("bus could not be retrieved");
    for msg in bus.iter_timed(gst::ClockTime::NONE) {
        use gst::MessageView;
        println!("message in bus");
        match msg.view() {
            MessageView::Qos(q) => {
                println!(" Got a QOS message: {:?}", q);
            }
            MessageView::Info(i) => {
                println!("Got an info message: {:?}", i);
            }
            MessageView::SegmentStart(s) => {
                println!("Got a segment start: {:?}", s)
            }
            MessageView::Latency(l) => {
                println!("Got a latency message: {:?}", l);
            }
            MessageView::Other => {
                println!("Got an other message:");
            }
            MessageView::Eos(..) => break,
            MessageView::Error(err) => {
                println!(
                    "Error from {:?}: {} ({:?})",
                    err.src().map(|s| s.path_string()),
                    err.error(),
                    err.debug()
                );
                break;
            }
            _ => (),
        }
    }

    pipeline
        .set_state(gst::State::Null)
        .expect("The pipeline had an error while being set to null");

    println!("Hello from receiver");
}
