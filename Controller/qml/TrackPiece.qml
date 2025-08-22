import QtQuick
import TrainView

Image {
    id: root

    signal add(int index)

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

    function snapToRotationPoint(fromConfig, toConfig, sibling, rotationOffset = 0) {
        let origin = sibling.mapToItem(area, fromConfig.point)

        root.x = origin.x - toConfig.point.x
        root.y = origin.y - toConfig.point.y

        root.railData.rotation_x = toConfig.point.x
        root.railData.rotation_y = toConfig.point.y

        root.railData.rotation += rotationOffset

        updateConnectors()
    }

    function connectToSibling() {
        const sibling = root.railData.connected_to[0]
        const index = root.railData.from_index

        root.railData.rotation = sibling ? sibling.railData.rotation : 0
        root.add.connect (function (index) {
            createTrackPiece(root, index)
        })

        if (!sibling) {
            return
        }

        const fromConfig = sibling.railData.connectors.get(index)
        const start = (fromConfig.dir === Globals.dir.start)
        root.railData.to_index = start ? 2 : 0
        const toConfig = root.railData.connectors.get(root.railData.to_index)
        const rotationOffset = (toConfig.angle - fromConfig.angle) * 22.5

        animation.enabled = false
        snapToRotationPoint(fromConfig, toConfig, sibling, rotationOffset)
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
            const index = root.railData.from_index
            const sibling = root.railData.connected_to[0]
            const fromConfig = sibling.railData.connectors.get(index)
            const start = (fromConfig.dir === Globals.dir.start)

            root.railData.to_index = root.railData.connectors.get(root.railData.to_index).next
            const toConfig = root.railData.connectors.get(root.railData.to_index)

            snapToRotationPoint(fromConfig, toConfig, sibling, toConfig.rotation)
        }
    }

    function flip() {
        if (!root.railData.flippable) {
            return
        }
    }

    Component.onCompleted: Globals.selectedTrack = root

    Repeater {
        model: root.railData.connectors
        delegate: RotationPointMarker {
            property Connector connector: model.object

            x: connector.point.x - width / 2
            y: connector.point.y - height / 2
        }
    }

    Rectangle {
        anchors.fill: parent
        visible: Globals.trackFrameVisible
        color: "transparent"
        border.width: 4
    }

    Rectangle {
        id: selectedMarker

        anchors.fill: parent
        anchors.margins: -radius / 2
        radius: 40
        z: 10
        visible: root.selected
        color: "transparent"
        opacity: 0.5
        border.width: 20
        border.color: "gold"
    }

    MouseArea {
        anchors.fill: parent
        onClicked: Globals.selectedTrack = (root.selected ? null : root)
    }

    Repeater {
        model: root.railData.connectors
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

    Behavior on x {
        enabled: animation.enabled
        NumberAnimation { duration: animation.duration; easing.type: animation.type }
    }

    Behavior on y {
        enabled: animation.enabled
        NumberAnimation { duration: animation.duration; easing.type: animation.type }
    }
}
