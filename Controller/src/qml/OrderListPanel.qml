import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import TrainView

Item {
    id: root

    property Train train

    implicitHeight: column.implicitHeight
    implicitWidth: 220

    ColumnLayout {
        id: column
        anchors.fill: parent
        spacing: 4

        Text {
            text: {
                var mode = root.train.control_mode === Train.Automatic ? "Automatic" : "Manual"
                return "Current stop: " + root.train.current_order_index + " · " + mode
            }
            font.bold: true
            Layout.fillWidth: true
            wrapMode: Text.WordWrap
        }

        ListView {
            id: orderView
            Layout.fillWidth: true
            Layout.preferredHeight: Math.min(160, Math.max(40, root.train.orders.count * 36))
            clip: true
            model: root.train.orders
            spacing: 2

            delegate: RowLayout {
                width: orderView.width
                height: 34
                spacing: 2

                required property var object
                required property int index

                Text {
                    text: index === root.train.current_order_index ? "\u25B6" : " "
                    Layout.preferredWidth: 14
                }

                Rectangle {
                    property color nodeColor: network.color_for_node(object.target_node_id)
                    visible: nodeColor.valid
                    color: nodeColor
                    border.width: 1
                    Layout.preferredWidth: 14
                    Layout.preferredHeight: 14
                }

                Text {
                    text: object.target_node_id
                    elide: Text.ElideRight
                    Layout.fillWidth: true
                }

                Text {
                    text: "wait"
                    font.pixelSize: 11
                    color: palette.mid
                }

                SpinBox {
                    id: waitSpin
                    from: 0
                    to: 999
                    editable: true
                    value: Math.round(object.wait_seconds)
                    Layout.preferredWidth: 72
                    ToolTip.visible: hovered
                    ToolTip.text: "Seconds to wait at this stop"
                    textFromValue: function(value, locale) { return value + "s" }
                    valueFromText: function(text, locale) {
                        return parseInt(String(text).replace("s", ""), 10) || 0
                    }
                    onValueModified: root.train.set_wait(index, value)
                }

                Button {
                    text: "\u2191"
                    enabled: index > 0
                    Layout.preferredWidth: 28
                    onClicked: root.train.move_order(index, index - 1)
                }

                Button {
                    text: "\u2193"
                    enabled: index < root.train.orders.count - 1
                    Layout.preferredWidth: 28
                    onClicked: root.train.move_order(index, index + 1)
                }

                Button {
                    text: "X"
                    Layout.preferredWidth: 28
                    onClicked: root.train.remove_order(index)
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 4

            ComboBox {
                id: markerPick
                Layout.fillWidth: true
                model: network.markerNodeIds
                enabled: count > 0
                currentIndex: count > 0 ? 0 : -1

                displayText: {
                    if (count === 0)
                        return "No markers"
                    if (currentIndex < 0)
                        return "Select marker…"
                    return currentText
                }

                delegate: ItemDelegate {
                    required property var modelData
                    required property int index
                    width: markerPick.width
                    highlighted: markerPick.highlightedIndex === index

                    contentItem: RowLayout {
                        spacing: 6

                        Rectangle {
                            property color nodeColor: network.color_for_node(modelData)
                            visible: nodeColor.valid
                            color: nodeColor
                            border.width: 1
                            Layout.preferredWidth: 12
                            Layout.preferredHeight: 12
                        }

                        Text {
                            text: modelData
                            elide: Text.ElideRight
                            Layout.fillWidth: true
                        }
                    }
                }

                contentItem: RowLayout {
                    spacing: 6
                    leftPadding: 8
                    rightPadding: markerPick.indicator.width + 8

                    Rectangle {
                        property color nodeColor: markerPick.currentIndex >= 0
                            ? network.color_for_node(markerPick.currentText)
                            : "transparent"
                        visible: markerPick.currentIndex >= 0 && nodeColor.valid
                        color: nodeColor
                        border.width: 1
                        Layout.preferredWidth: 12
                        Layout.preferredHeight: 12
                    }

                    Text {
                        text: markerPick.displayText
                        elide: Text.ElideRight
                        Layout.fillWidth: true
                        verticalAlignment: Text.AlignVCenter
                    }
                }
            }

            Button {
                text: "Add"
                enabled: markerPick.currentIndex >= 0 && markerPick.count > 0
                onClicked: root.train.add_order(markerPick.currentText, 0)
            }

            Button {
                text: "Clear"
                enabled: root.train.orders.count > 0
                onClicked: root.train.clear_orders()
            }
        }

        Text {
            visible: network.markerNodeIds.length === 0
            text: "Generate network to list markers"
            font.pixelSize: 11
            color: palette.mid
            Layout.fillWidth: true
            wrapMode: Text.WordWrap
        }
    }
}
