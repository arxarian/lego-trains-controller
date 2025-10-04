import QtQuick
import TrainView

Item
{
    id: root

    property var model

    Repeater {
        model: root.model
        delegate: MarkerItem {
            marker: model.object
        }
    }
}
