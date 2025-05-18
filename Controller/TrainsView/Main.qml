import QtQuick
import QtQuick.Controls

ApplicationWindow {
    visible: true
    width: 400
    height: 300
    title: "Lego Trains Controller"
    color: "lightblue"

    Item {
        anchors.fill: parent

        Column {
            anchors.fill: parent
            Text {
                text: "Welcome to Lego Trains Contoller!"
                font.pixelSize: 24
            }

            Button {
                text: "Discover"
                onClicked: {
                    discoveredDevices.open()
                    devices.discover()
                }
            }

            Button {
                text: "Connect"
                onClicked: devices.connect_to("Pybricks Hub")
            }

            Button {
                text: "Disconnect"
                onClicked: devices.firstDevice().disconnect()
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

            Button {
                text: "Voltage"
                onClicked: devices.firstDevice().send("vol")
            }

            Rectangle {
                id: detectedColor
                width: 50
                height: 50
                border.width: 2
                // color: devices.firstDevice().color

                MouseArea { // TODO - remove this hack
                    anchors.fill: parent
                    onClicked: {
                        parent.color = Qt.binding(function() {return devices.firstDevice().color})
                    }
                }
            }
        }
    }

    DiscoverDevices {
        id: discoveredDevices
        anchors.centerIn: Overlay.overlay
        height: Overlay.overlay.height - 40
        width: Overlay.overlay.width - 40
    }
}
