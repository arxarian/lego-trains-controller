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
        root.add.connect (function (index) {
            createTrackPiece(root, index)
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
