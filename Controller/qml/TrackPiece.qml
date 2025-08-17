import QtQuick
import TrainView

Image {
    id: root

    signal add(int index)

    readonly property bool selected: Globals.selectedTrack === root

    required property list<RotationData> rotationData
    required property Rail railData

    z: Globals.selectedTrack === root ? 10 : 0

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

    function snapToRotationPoint(fromConfig, toConfig, sibling) {

        let origin = sibling.mapToItem(area, fromConfig.point)

        root.railData.rotation_x = toConfig.point.x
        root.railData.rotation_y = toConfig.point.y

        toConfig.visible = false

        root.x = origin.x - toConfig.point.x
        root.y = origin.y - toConfig.point.y

        const start = (fromConfig.dir === Globals.dir.start)
        let angle = start ? -fromConfig.angle : toConfig.angle
        root.railData.rotation += angle * 22.5

    }

    function connectTo(sibling, index = 0) {
        root.railData.rotation = sibling ? sibling.railData.rotation : 0
        root.add.connect (function (index) {
            createTrackPiece(root, index)
        })

        if (!sibling) {
            return;
        }

        const fromConfig = sibling.rotationData[index]
        const start = (fromConfig.dir === Globals.dir.start)
        const toConfig = root.rotationData[start ? 2 : 0]

        console.log("from", fromConfig.dir, "index", index)
        console.log("to", toConfig)

        snapToRotationPoint(fromConfig, toConfig, sibling)
    }


    function rotate() {
        if (railData.connected_to.length === 0) {
            root.railData.rotation_x = root.width / 2
            root.railData.rotation_y = root.height / 2
            root.railData.rotation = root.railData.rotation + 22.5
        } else if (railData.connected_to.length === 1) {
            console.warn("reconnect in progress")

            //
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

            rotation: config ? (config.angle * -22.5) : 0
            transformOrigin: Item.TopLeft
            visible: config ? (config.visible && !config.objectName.endsWith("_flipped") ) : false
            x: config ? config.point.x : 0
            y: config ? config.point.y - (config.dir === Globals.dir.start ? 0 : height) : 0
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
