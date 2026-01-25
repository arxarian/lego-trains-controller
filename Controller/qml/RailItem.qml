import QtQuick
import TrainView

SelectableItem {
    id: root

    /*required*/ property Rail railData // TODO - required is not working for some reason
    property alias connectors: connectors   // TODO - is it necessary?

    x: root.railData ? root.railData.x : 0
    y: root.railData ? root.railData.y : 0

    width: image.sourceSize.width
    height: image.sourceSize.height
    propagateComposedEvents: true

    deleteAction: function() {
        rails.remove(root.railData)
    }

    rotateAction: function() {
        root.rotate()
    }

    Image {
        id: image
        source: root.railData ? root.railData.source : ""
    }

    QtObject {
        id: animation
        property bool enabled: false
        property real duration: 600
        property int type: Easing.InOutQuad
    }

    transform: Rotation {
        id: transformation
        property Rotator rotator: root.railData ? root.railData.rotator : undefined
        origin.x: transformation.rotator ? transformation.rotator.x : 0
        origin.y: transformation.rotator ? transformation.rotator.y : 0
        angle: transformation.rotator ? transformation.rotator.angle : 0

        Behavior on angle {
            enabled: animation.enabled
            NumberAnimation { duration: animation.duration; easing.type: animation.type }
        }

        Behavior on origin.x {
            enabled: animation.enabled
            NumberAnimation { duration: animation.duration; easing.type: animation.type }
        }

        Behavior on origin.y {
            enabled: animation.enabled
            NumberAnimation { duration: animation.duration; easing.type: animation.type }
        }
    }

    function snapToRotationPoint(fromConnector, toConnector, sibling, rotationOffset = 0) {
        let origin = sibling.mapToItem(area, Qt.point(fromConnector.rotator.x, fromConnector.rotator.y))

        root.railData.x = origin.x - toConnector.rotator.x
        root.railData.y = origin.y - toConnector.rotator.y
        root.railData.rotator.x = toConnector.rotator.x
        root.railData.rotator.y = toConnector.rotator.y
        root.railData.rotator.angle += rotationOffset
    }

    function positionTrackToSibling() {
        const siblings = rails.findsiblingsOf(root.railData.id)

        if (siblings.length === 0) {
            return
        }

        const siblingId = siblings[0]
        const siblingData = rails.findRailData(siblingId)
        const fromConnector = siblingData.connectors.findFromConnector(root.railData.id)

        const toConnector = root.railData.connectors.getFirstConnected()
        const rotationOffset = (toConnector.angle - fromConnector.angle) * 22.5

        root.railData.rotator.angle = siblingData.rotator.angle

        const siblingItem = rails.findRailItem(siblingId)

        animation.enabled = false
        snapToRotationPoint(fromConnector, toConnector, siblingItem, rotationOffset)
        animation.enabled = true
    }

    function rotate() {
        if (root.railData.connectors.activeCount() === 0) {
            root.railData.rotator.x = root.width / 2
            root.railData.rotator.y = root.height / 2
            root.railData.rotator.angle = root.railData.rotator.angle + 22.5
        } else if (root.railData.connectors.activeCount() === 1) {
            // TODO - no need to have a real sibling here
            const siblingId = rails.findsiblingsOf(root.railData.id)[0] // return the first sibling
            const siblingData = rails.findRailData(siblingId)
            const fromConnector = siblingData.connectors.findFromConnector(root.railData.id)
            const toConnector = root.railData.connectors.setNextConnector()

            const siblingItem = rails.findRailItem(siblingId)
            snapToRotationPoint(fromConnector, toConnector, siblingItem, toConnector.rotator.angle)
        }
        // cannot rotate more connected
    }

    Component.onCompleted: {
        rails.registerRail(root, root.railData.id)

        if (!rails.loading) {
            root.positionTrackToSibling()
        }

        root.forceActiveFocus()

        rails.checkLoaded()
    }

    RotationPoints {
        anchors.fill: parent
        model: root.railData.connectors
    }

    Rectangle {
        anchors.fill: parent
        visible: Globals.trackFrameVisible
        color: "transparent"
        border.width: 4
    }

    Connectors {
        id: connectors
        anchors.fill: parent
        railId: root.railData.id
        model: root.railData.connectors
    }

    MarkerView {
        id: markers
        anchors.fill: parent
        model: root.railData.markers
    }

    Behavior on x {
        enabled: animation.enabled
        NumberAnimation { duration: animation.duration; easing.type: animation.type }
    }

    Behavior on y {
        enabled: animation.enabled
        NumberAnimation { duration: animation.duration; easing.type: animation.type }
    }

    Text {
        visible: Globals.railIdVisible
        anchors.centerIn: parent
        font.pixelSize: 150
        font.bold: true
        color: "gold"
        text: root.railData.id
        rotation: 360 - root.railData.rotator.angle
    }

    MouseArea {
        id: mouse
        anchors.fill: parent
        propagateComposedEvents: true
        onClicked: (mouse) => {
            mouse.accepted = false
            console.log("rail id", root.railData.id)
        }
    }

    PathIndicatorView {
        anchors.fill: parent
        model: PathIndicatorsFilter {
            id: filter
            sourceModel: root.railData.path_indicators
            path_id: "A"
        }
    }
}
