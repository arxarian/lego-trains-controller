import QtQuick
import TrainView

Image {
    id: root

    required property Rail railData
    readonly property bool selected: Globals.selectedTrack === root

    z: root.selected === root ? 10 : 0

    source: root.railData ? root.railData.source : ""

    QtObject {
        id: animation
        property bool enabled: false
        property real duration: 600
        property int type: Easing.InOutQuad
    }

    transform: Rotation {
        id: transformation
        origin.x: root.railData ? root.railData.rotation_x : 0
        origin.y: root.railData ? root.railData.rotation_y : 0
        angle: root.railData ? root.railData.rotation : 0

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

    function updateConnectors() {
        let dir = root.railData.connectors.get(root.railData.to_index).dir
        for (let i = 0; i < root.railData.connectors.rowCount(); ++i) {
            let connector = root.railData.connectors.get(i)
            connector.visible = (dir !== connector.dir)
        }
    }

    function snapToRotationPoint(fromConnector, toConnector, sibling, rotationOffset = 0) {
        let origin = sibling.mapToItem(area, fromConnector.point)

        console.log(JSON.stringify(fromConnector), "\n", JSON.stringify(toConnector))

        root.x = origin.x - toConnector.point.x
        root.y = origin.y - toConnector.point.y

        root.railData.rotation_x = toConnector.point.x
        root.railData.rotation_y = toConnector.point.y

        root.railData.rotation += rotationOffset

        updateConnectors()
    }

    function connectToSibling() {
        const sibling = root.railData.connected_to[0]
        const index = root.railData.from_index

        root.railData.rotation = sibling ? sibling.railData.rotation : 0
        connectors.add.connect (function (index) {
            createTrackPiece(root, index)   // TODO - calling a function from TrackEditor, that's a bit wierd
        })

        if (!sibling) {
            return
        }

        const fromtoConnector = sibling.railData.connectors.get(index)
        const start = (fromtoConnector.dir === Globals.dir.start)
        root.railData.to_index = start ? 2 : 0
        const totoConnector = root.railData.connectors.get(root.railData.to_index)
        const rotationOffset = (totoConnector.angle - fromtoConnector.angle) * 22.5

        animation.enabled = false
        snapToRotationPoint(fromtoConnector, totoConnector, sibling, rotationOffset)
        animation.enabled = true
    }

    function rotate() {
        if (!root.railData.rotatable) {
            return
        }

        if (root.railData.connected_to.length === 0) {
            root.railData.rotation_x = root.width / 2
            root.railData.rotation_y = root.height / 2
            root.railData.rotation = root.railData.rotation + 22.5
        } else if (root.railData.connected_to.length === 1) {
            const sibling = root.railData.connected_to[0]
            const fromConnector = sibling.railData.connectors.get(root.railData.from_index)

            root.railData.to_index = root.railData.connectors.get(root.railData.to_index).next
            const toConnector = root.railData.connectors.get(root.railData.to_index)

            snapToRotationPoint(fromConnector, toConnector, sibling, toConnector.rotation)
        }
    }

    function flip() {
        if (!root.railData.flippable) {
            return
        }
    }

    Component.onCompleted: Globals.selectedTrack = root

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
        onClicked: Globals.selectedTrack = (root.selected ? null : root)
    }

    Connectors {
        id: connectors
        anchors.fill: parent
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
