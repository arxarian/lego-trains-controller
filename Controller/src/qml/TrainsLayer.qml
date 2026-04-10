import QtQuick
import TrainView

Item {
    id: root

    property var model

    Repeater {
        model: root.model
        delegate: TrainItem {
            trainData: model.object
        }
    }
}
