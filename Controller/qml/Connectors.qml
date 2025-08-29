import QtQuick
import TrainView

Item
{
    id: root

    property int railId: -1
    property var model  // TODO - why var and not Connectors?
    signal clicked(int railId, int index)

    Repeater {
        model: root.model
        delegate: Rectangle {
            id: item
            property Connector connector: model.object
            property bool reversed: connector.dir === Globals.dir.start

            rotation: item.connector.angle * -22.5
            transformOrigin: item.reversed ? Item.BottomLeft : Item.TopLeft  // TODO - not working
            visible: item.connector.visible && !item.connector.name.endsWith("_flipped")
            x: item.connector.rotator.x
            y: item.connector.rotator.y - (item.reversed ? 0 : height)
            width: 320
            height: 50

            color: "#55FF00FF"

            MouseArea {
                anchors.fill: parent
                onClicked: root.clicked(root.railId, index)
            }
        }
    }
}
