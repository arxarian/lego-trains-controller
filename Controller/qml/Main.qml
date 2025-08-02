import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    visible: true
    width: 800
    height: 800
    title: "Lego Trains Controller"
    color: "lightblue"

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        Text {
            Layout.preferredHeight: contentHeight + 5
            Layout.fillWidth: true

            text: "Welcome to Lego Trains Contoller!"
            font.pixelSize: 24
            horizontalAlignment: Text.AlignHCenter

            Rectangle {
                z: -1
                anchors.fill: parent
                color: "gold"
            }
        }

        Row {
            Layout.preferredHeight: discoverButton.availableHeight * 1.5
            Layout.fillWidth: true

            Button {
                id: discoverButton
                text: "Discover"
                onClicked: {
                    discoveredDevices.open()
                    devices.discover()
                }
            }

            Button {
                text: "Connect to Pybricks Hub"
                onClicked: devices.connect_to("Pybricks Hub")
            }

            Button {
                text: "Connect to Express Train"
                onClicked: devices.connect_to("Express Train")
            }
        }

        StackLayout {
            z: -1
            currentIndex: trainView.count > 0 ? 1 : 0
            Layout.fillHeight: true
            Layout.fillWidth: true

            TrackEditor {}

            ListView {
                id: trainView
                model: devices
                orientation: Qt.Horizontal

                delegate: TrainControlPanel {
                    height: trainView.height
                    width: 70
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
