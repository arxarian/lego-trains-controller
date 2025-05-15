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
                text: "Hello from QML"
                font.pixelSize: 24
            }

            Button {
                text: "Connect"
                onClicked: devices.connect_to("Pybricks Hub")
            }

            Button {
                text: "FWD"
                onClicked: devices.send("fwd")
            }

        }
    }
}
