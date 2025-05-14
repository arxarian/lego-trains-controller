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

        Text {
            anchors.centerIn: parent
            text: "Hello from QML"
            font.pixelSize: 24
        }

        Button {
            text: "Click me"
            onClicked: devices.connect_to("Pybricks Hub")
        }
    }
}
