import QtQuick
import QtQuick.Controls

ApplicationWindow {
    visible: true
    width: 400
    height: 300
    title: "Lego Trains Controller"

    Rectangle {
        anchors.fill: parent
        color: "lightblue"

        Column {
            anchors.fill: parent
            Text {
                text: "Welcome to Lego Trains Contoller!"
                font.pixelSize: 24
            }

            Button {
                text: "Connect"
                onClicked: devices.connect_to("Pybricks Hub")
            }

            Button {
                text: "Forward"
                onClicked: devices.firstDevice().send("fwd")
            }

            Button {
                text: "Reverse"
                onClicked: devices.firstDevice().send("rev")
            }

            Button {
                text: "Stop"
                onClicked: devices.firstDevice().send("stp")
            }

        }
    }
}
