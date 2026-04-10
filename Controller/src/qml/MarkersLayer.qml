import QtQuick
import TrainView

Item {
    id: root

    property var model

    Repeater {
        model: root.model
        delegate: Item {
            property Rail railData: model.object
            x: railData ? railData.x : 0
            y: railData ? railData.y : 0

            transform: Rotation {
                property Rotator rotator: railData ? railData.rotator : undefined
                origin.x: rotator ? rotator.x : 0
                origin.y: rotator ? rotator.y : 0
                angle: rotator ? rotator.angle : 0
            }

            MarkerView {
                model: railData ? railData.markers : undefined
            }
        }
    }
}
