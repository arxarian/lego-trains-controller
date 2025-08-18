import QtQuick
import TrainView

Image {
    id: root

    signal add(int index)

    readonly property bool selected: Globals.selectedTrack === root

    required property list<RotationData> rotationData
    required property Rail railData

    z: root.selected === root ? 10 : 0

    transform: Rotation {
        id: transformation
        origin.x: root.railData ? root.railData.rotation_x : 0
        origin.y: root.railData ? root.railData.rotation_y : 0
        angle: root.railData ? root.railData.rotation : 0
    }

    // SequentialAnimation {
    //     id: animation
    //     running: false
    //     RotationAnimator {
    //         target: transformation
    //         property: "angle"
    //         from: 0
    //         to: 180
    //         duration: 200
    //     }
    // }

    // Behavior on transform.angle {
    //     RotationAnimator {
    //         direction: RotationAnimation.Clockwise
    //         duration : 200
    //     }
    // }

    // Behavior on rotation {
    //     RotationAnimator {
    //         direction: RotationAnimation.Clockwise
    //         duration : 200
    //     }
    // }

    function snapToRotationPoint(fromConfig, toConfig, sibling, rotationOffset = 0) {
        let origin = sibling.mapToItem(area, fromConfig.point)

        root.railData.rotation_x = toConfig.point.x
        root.railData.rotation_y = toConfig.point.y

        root.x = origin.x - toConfig.point.x
        root.y = origin.y - toConfig.point.y

        root.railData.rotation += rotationOffset

        updateConnectors()
    }

    function updateConnectors() {
        let dir = root.rotationData[root.railData.to_index].dir
        root.rotationData.forEach((element) => {element.visible = (dir !== element.dir)})
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

        const fromConfig = sibling.rotationData[index]
        const start = (fromConfig.dir === Globals.dir.start)
        root.railData.to_index = start ? 2 : 0
        const toConfig = root.rotationData[root.railData.to_index]
        const rotationOffset = (toConfig.angle - fromConfig.angle) * 22.5

        snapToRotationPoint(fromConfig, toConfig, sibling, rotationOffset)
    }


    function rotate() {
        if (root.railData.connected_to.length === 0) {
            root.railData.rotation_x = root.width / 2
            root.railData.rotation_y = root.height / 2
            root.railData.rotation = root.railData.rotation + 22.5
        } else if (root.railData.connected_to.length === 1) {
            const sibling = root.railData.connected_to[0]
            const index = root.railData.from_index
            const fromConfig = sibling.rotationData[index]
            const start = (fromConfig.dir === Globals.dir.start)

            root.railData.to_index = root.rotationData[root.railData.to_index].flipped
            const toConfig = root.rotationData[root.railData.to_index]

            let rotationOffset = 0
            if (root.railData.type === Rail.Straight) {
                rotationOffset = 180
            } else if (root.railData.type === Rail.Curved) {
                const sign = toConfig.angle > 0 ? -1 : 1
                rotationOffset = sign * (180 - 22.5)
            }

            snapToRotationPoint(fromConfig, toConfig, sibling, rotationOffset)
        }
    }

    function flip() {
        console.warn("flip not implemented")
    }

    Component.onCompleted: Globals.selectedTrack = root

    Repeater {
        model: root.rotationData.length
        delegate: RotationPointMarker {
            x: rotationData[index].point.x - width / 2
            y: rotationData[index].point.y - height / 2
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
        model: root.rotationData.length
        delegate: Rectangle {
            property RotationData config: rotationData[index]

            property bool reversed: config ? config.dir === Globals.dir.start : true

            rotation: config ? (config.angle * -22.5) : 0
            transformOrigin: reversed ? Item.BottomLeft : Item.TopLeft  // TODO - not working
            visible: config ? (config.visible && !config.objectName.endsWith("_flipped")) : false
            x: config ? config.point.x : 0
            y: config ? (config.point.y - (reversed ? 0 : height)) : 0
            width: 320
            height: 50

            color: "#55FF00FF"

            MouseArea {
                anchors.fill: parent
                onClicked: {
                    root.add(index)
                    config.visible = false
                }
            }
        }
    }
}
