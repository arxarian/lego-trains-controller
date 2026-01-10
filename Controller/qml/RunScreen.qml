import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 5
        spacing: 0

        RowLayout {
            Layout.preferredHeight: 25
            Layout.fillWidth: true

            Button {
                id: discoverButton
                text: "Discover"
                onClicked: devices.discover()
            }

            Button {
                text: "Connect to Pybricks Hub"
                onClicked: devices.connect_to("Pybricks Hub")
            }

            Button {
                text: "Connect to Express Train"
                onClicked: devices.connect_to("Express Train")
            }

            Item {
                Layout.fillWidth: true
            }

            Button {
                text: "Generate big graph"
                onClicked: {
                    projectStorage.loadProject("rails_big")    // DEBUG - remove
                    network.generate(rails)
                }
            }

            Button {
                text: "Generate small graph"
                onClicked: {
                    projectStorage.loadProject("rails")    // DEBUG - remove
                    network.generate(rails)
                }
            }

        }

        ListView {
            id: trainView

            Layout.fillHeight: true
            Layout.fillWidth: true
            Layout.margins: 10

            model: devices
            orientation: Qt.Horizontal

            delegate: TrainControlPanel {
                height: trainView.height
                width: 100
            }
        }
    }
}
