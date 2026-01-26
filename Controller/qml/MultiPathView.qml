import QtQuick
import TrainView

Item {
    id: root
    property var model

    Repeater {
        model: root.model.multiPathIndicators

        delegate: Item {
            id: item

            property MultiPathIndicator indicator: model.object

            width: root.width
            height: root.height

            PathIndicatorView {
                anchors.fill: parent
                model: PathIndicatorsFilter {
                    id: filter
                    sourceModel: root.model // TODO - it's a bit confusing to use the same model as above
                    path_id: item.indicator.path_id
                }
            }
        }
    }
}
