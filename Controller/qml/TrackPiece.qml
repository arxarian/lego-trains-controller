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
        origin.x: root.railData ? root.railData.rotation_x : 0
        origin.y: root.railData ? root.railData.rotation_y : 0
        angle: root.railData ? root.railData.rotation : 0
    }

    Component.onCompleted: Globals.selectedTrack = root

    Shortcut {
        enabled: root.selected
        sequences: ["F"]
        onActivated: console.warn("flip not implemented")
    }

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
