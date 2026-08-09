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
                return "Orders idx " + root.train.current_order_index + " · " + mode
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

                SpinBox {
                    id: waitSpin
                    from: 0
                    to: 999
                    editable: true
                    value: Math.round(object.wait_seconds)
                    Layout.preferredWidth: 70
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

            TextField {
                id: debugNodeId
                placeholderText: "node id"
                Layout.fillWidth: true
            }

            Button {
                text: "Add"
                enabled: debugNodeId.text.trim().length > 0
                onClicked: {
                    root.train.add_order(debugNodeId.text.trim(), 0)
                    debugNodeId.text = ""
                }
            }

            Button {
                text: "Clear"
                enabled: root.train.orders.count > 0
                onClicked: root.train.clear_orders()
            }
        }
    }
}
