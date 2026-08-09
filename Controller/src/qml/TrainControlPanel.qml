import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import TrainView

Item {
    id: root

    property Train train: model.object
    property var device: root.train.device
    property int trainIndex: 0

    readonly property bool isPlanningTarget: Globals.planningTrainIndex === trainIndex

    Rectangle {
        anchors.fill: parent
        color: root.isPlanningTarget ? "#cce5ff" : "transparent"
        border.color: root.isPlanningTarget ? "#6699cc" : "transparent"
        border.width: 2
        radius: 4
    }

    function selectAsPlanningTarget() {
        Globals.planningTrainIndex = root.trainIndex
        if (ListView.view)
            ListView.view.currentIndex = root.trainIndex
    }

    TapHandler {
        acceptedButtons: Qt.LeftButton
        gesturePolicy: TapHandler.DragThreshold
        onTapped: root.selectAsPlanningTarget()
    }

    ScrollView {
        anchors.fill: parent
        anchors.margins: 2
        contentWidth: availableWidth
        clip: true

        GroupBox {
            title: root.device.name + (root.isPlanningTarget ? " (planning)" : "")
            enabled: root.device.initialized
            width: root.width - 8

            ColumnLayout {
                width: parent.width
                spacing: 4

                Text {
                    text: "Speed " + speedSlider.value
                    Layout.alignment: Qt.AlignHCenter
                }

                Slider {
                    id: speedSlider

                    value: root.device.speed
                    orientation: Qt.Vertical
                    wheelEnabled: true
                    from: root.device.minimalSpeed
                    to: 100
                    stepSize: 10
                    snapMode: Slider.SnapAlways

                    Layout.alignment: Qt.AlignHCenter
                    Layout.preferredHeight: 80

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

                    Layout.preferredHeight: 36
                    Layout.preferredWidth: 36
                    Layout.alignment: Qt.AlignHCenter
                }

                Text {
                    text: "Segment:"
                    font.bold: true
                    Layout.alignment: Qt.AlignHCenter
                }

                Text {
                    text: root.train.current_segment_id || "unknown"
                    wrapMode: Text.WrapAnywhere
                    horizontalAlignment: Text.AlignHCenter
                    Layout.fillWidth: true
                }

                OrderListPanel {
                    train: root.train
                    Layout.fillWidth: true
                    Layout.preferredHeight: implicitHeight
                }
            }
        }
    }
}
