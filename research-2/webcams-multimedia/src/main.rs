use common::common::encoding_tuple;
use gst::prelude::*;
use gstreamer::{self as gst};
use std::process::Command;
mod common;
fn get_selected_device_from_user() -> Option<String> {
    let res = Command::new("v4l2-ctl")
        .arg("--list-devices")
        .output()
        .expect("Something went wrong while listing devices with v4l2-ctl");

    return Some("/dev/video0".to_string());
}

struct VideoPipeline {
    encoding_part: String,
}

fn main() {
    gst::init().unwrap();
    let video_capture = gst::ElementFactory::make("v4l2src")
        .name("camera")
        .property("device", "/dev/video0")
        .build()
        .expect("Could not make v4l2src element");

    let video_convert = gst::ElementFactory::make("videoconvert")
        .name("converter")
        .build()
        .expect("videoconvert could not be made");

    let (video_encoder, rtppay) = encoding_tuple();
    let port: i32 = 2001;
    let udp_sink = gst::ElementFactory::make("udpsink")
        .name("network-comm")
        .property("host", "127.0.0.1")
        .property("port", port)
        .build()
        .expect("udpsink could not be made");

    let pipeline = gst::Pipeline::with_name("Video Source Pipeline");
    pipeline
        .add_many([
            &video_capture,
            &video_convert,
            &video_encoder,
            &rtppay,
            &udp_sink,
        ])
        .unwrap();
    gst::Element::link_many([
        &video_capture,
        &video_convert,
        &video_encoder,
        &rtppay,
        &udp_sink,
    ]);

    video_capture.connect_pad_added(move |src, src_pad| {
        println!("received new pad {} from {}", src_pad.name(), src.name());

        let sink_pad = video_convert
            .static_pad("sink")
            .expect("Failed to get static sink pad from convert");
        if sink_pad.is_linked() {
            println!("We are already linked. Ignoring.");
            return;
        }

        let new_pad_caps = src_pad
            .current_caps()
            .expect("Failed to get caps of new pad.");

        let new_pad_struct = new_pad_caps
            .structure(0)
            .expect("Failed to get first structure of caps.");

        let new_pad_type = new_pad_struct.name();
        let is_video = new_pad_type.starts_with("video/x-raw");
        if !is_video {
            println!("It has type {new_pad_type} which is not raw video. Ignoring.");
            return;
        }

        let res = src_pad.link(&sink_pad);
        if res.is_err() {
            println!("Type is {new_pad_type} but link failed");
        } else {
            println!("Link succeeded (type {new_pad_type}).");
        }
    });

    println!("Hello, world!");

    println!("This mini app will demonstrate the differences between different multimedia configurations in terms of e2e latency");

    let video_device =
        get_selected_device_from_user().expect("Something went wrong with device usage");

    pipeline
        .set_state(gst::State::Playing)
        .expect("Unable to set the pipeline to the `Playing` state");

    let bus = pipeline.bus().unwrap();

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
                println!("Got a latency message: {:?}", l)
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
        .expect("Unable to set the pipeline to the `Null` state");
}
