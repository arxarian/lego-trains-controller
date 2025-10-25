import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import TrainView

Item {
    id: root

    property Device device: model.object

    GroupBox {
        title: root.device.name
        enabled: root.device.initialized

        ColumnLayout {
            anchors.fill: parent

            Button {
                text: "Disconnect"
                onClicked: root.device.disconnect()
                Layout.fillWidth: true
            }

            Button {
                text: "Shut down"
                onClicked: root.device.shutDown()
                Layout.fillWidth: true
            }

            Text {
                text: "Speed " + speedSlider.value
                Layout.alignment: Qt.AlignHCenter
            }

            Slider {
                id: speedSlider

                orientation: Qt.Vertical
                wheelEnabled: true
                from: -100
                to: 100
                stepSize: 10
                snapMode: Slider.SnapAlways

                Layout.alignment: Qt.AlignHCenter

                Binding {
                    target: root.device
                    property: "speed"
                    value: speedSlider.value
                }
            }

            Button {
                text: "Stop"
                onClicked: speedSlider.value = 0
                Layout.fillWidth: true
            }

            Text {
                text: "Voltage " + (root.device.voltage / 1000).toFixed(1) + " V"
                Layout.alignment: Qt.AlignHCenter
            }

            Rectangle {
                id: detectedColor
                border.width: 2
                color: root.device.color

                Layout.preferredHeight: 50
                Layout.preferredWidth: 50
                Layout.alignment: Qt.AlignHCenter
            }
        }
    }
}
