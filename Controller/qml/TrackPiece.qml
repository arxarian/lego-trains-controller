import QtQuick
import TrainView

Image {
    id: root

    /*required*/ property Rail railData // TODO - required is not working for some reason
    readonly property bool selected: root.activeFocus
    property alias connectors: connectors

    x: root.railData ? root.railData.x : 0
    y: root.railData ? root.railData.y : 0
    z: root.selected ? 10 : 0

    focus: true
    source: root.railData ? root.railData.source : ""

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

        const start = (fromConnector.dir === Globals.dir.start)
        const toConnector = root.railData.connectors.get(0)
        const rotationOffset = (toConnector.angle - fromConnector.angle) * 22.5

        root.railData.rotator.angle = siblingData.rotator.angle + (start ? 180 : 0)

        const siblingItem = rails.findRailItem(siblingId)

        animation.enabled = false
        snapToRotationPoint(fromConnector, toConnector, siblingItem, rotationOffset)
        animation.enabled = true
    }

    function rotate() {
        if (root.railData.connectors.connections() === 0) {
            root.railData.rotator.x = root.width / 2
            root.railData.rotator.y = root.height / 2
            root.railData.rotator.angle = root.railData.rotator.angle + 22.5
        } else if (root.railData.connectors.connections() === 1) {
            // TODO - no need to have a real sibling here
            const siblingId = rails.findsiblingsOf(root.railData.id)[0] // return the first sibling
            const siblingData = rails.findRailData(siblingId)
            const fromConnector = siblingData.connectors.findFromConnector(root.railData.id)
            const toConnector = root.railData.connectors.getAndSetNextConnector()

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

    Keys.onPressed: (event)=> {
                        if (event.key === Qt.Key_Delete) {
                            rails.remove(root.railData)
                            event.accepted = true
                        } else if (event.key === Qt.Key_R) {
                            root.rotate()
                            event.accepted = true
                        }
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

    SelectedMarker {
        anchors.fill: parent
        anchors.margins: -radius / 2
        z: 10
        visible: root.selected
    }

    MouseArea {
        anchors.fill: parent
        propagateComposedEvents: true
        onClicked: function(mouse) {
            mouse.accepted = false
            root.forceActiveFocus()
        }
    }

    Connectors {
        id: connectors
        anchors.fill: parent
        railId: root.railData.id
        model: root.railData.connectors
    }

    Behavior on x {
        enabled: animation.enabled
        NumberAnimation { duration: animation.duration; easing.type: animation.type }
    }

    Behavior on y {
        enabled: animation.enabled
        NumberAnimation { duration: animation.duration; easing.type: animation.type }
    }
}
