import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import TrainView

Item {
    id: root

    property Train train: model.object
    property var device: root.train ? root.train.device : null
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
            title: root.device
                   ? root.device.name + (root.isPlanningTarget ? " (planning)" : "")
                   : ""
            enabled: root.device ? root.device.initialized : false
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

                    value: root.device ? root.device.speed : 0
                    orientation: Qt.Vertical
                    wheelEnabled: true
                    from: root.device ? root.device.minimalSpeed : 0
                    to: 100
                    stepSize: 10
                    snapMode: Slider.SnapAlways
                    enabled: root.train && root.train.control_mode !== Train.Automatic

                    Layout.alignment: Qt.AlignHCenter
                    Layout.preferredHeight: 80

                    Binding {
                        target: root.device
                        property: "speed"
                        value: speedSlider.value
                        when: root.device !== null && (!root.train || root.train.control_mode !== Train.Automatic)
                    }
                }

                Button {
                    text: root.train && root.train.halted_by_stop ? "Resume" : "Stop"
                    highlighted: root.train && root.train.halted_by_stop
                    onClicked: {
                        if (root.train)
                            root.train.toggle_stop()
                    }
                    Layout.fillWidth: true
                }

                Text {
                    text: root.device
                          ? "Voltage " + (root.device.voltage / 1000).toFixed(1) + " V"
                          : "Voltage —"
                    Layout.alignment: Qt.AlignHCenter
                }

                Rectangle {
                    id: detectedColor
                    border.width: 2
                    color: root.device ? root.device.color : "transparent"

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
                    text: root.train
                          ? (root.train.current_segment_id || "unknown")
                          : "unknown"
                    wrapMode: Text.WrapAnywhere
                    horizontalAlignment: Text.AlignHCenter
                    Layout.fillWidth: true
                }

                OrderListPanel {
                    train: root.train
                    Layout.fillWidth: true
                    Layout.preferredHeight: implicitHeight
                    visible: root.train !== null
                }
            }
        }
    }
}
