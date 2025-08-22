import QtQuick
import TrainView

Item
{
    id: root

    property var model  // TODO - why var and not Connectors?
    signal add(int index)

    Repeater {
        model: root.model
        delegate: Rectangle {
            property Connector connector: model.object
            property bool reversed: connector.dir === Globals.dir.start

            rotation: connector.angle * -22.5
            transformOrigin: reversed ? Item.BottomLeft : Item.TopLeft  // TODO - not working
            visible: connector.visible && !connector.name.endsWith("_flipped")
            x: connector.point.x
            y: connector.point.y - (reversed ? 0 : height)
            width: 320
            height: 50

            color: "#55FF00FF"

            MouseArea {
                anchors.fill: parent
                onClicked: {
                    root.add(index)
                    connector.visible = false
                }
            }
        }
    }
}
