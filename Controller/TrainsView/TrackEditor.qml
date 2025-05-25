import QtQuick
import QtQuick.Controls
Item {
    id: root

    property real scaleFactor: 0.2
    property real minimalScale: 0.05
    property real maximalScale: 3

    property int trackType: 0

    MouseArea {
        id: mouseArea

        property real offsetX: 0
        property real offsetY: 0
        property real startX: 0
        property real startY: 0

        anchors.fill: parent
        onPressed: (mouse) => {
            mouseArea.startX = area.x
            mouseArea.startY = area.y
            mouseArea.offsetX = mouse.x
            mouseArea.offsetY = mouse.y
        }
        onPositionChanged: (mouse) => {
            area.x = mouse.x - mouseArea.offsetX + mouseArea.startX
            area.y = mouse.y - mouseArea.offsetY + mouseArea.startY
        }
    }

    Row {
        anchors.top: parent.top
        anchors.topMargin: 50
        anchors.right: parent.right
        anchors.rightMargin: 20

        Button {
            checked: root.trackType === 0
            checkable: true
            text: "Straight"
            onClicked: root.trackType = 0
        }

        Button {
            checked: root.trackType === 1
            checkable: true
            text: "Curved"
            onClicked: root.trackType = 1
        }

        Button {
            checked: root.trackType === 2
            checkable: true
            text: "Switch"
            onClicked: root.trackType = 2
        }
    }

    WheelHandler {
        id: wheel
        onWheel: (event) => {
            if (event.angleDelta.y > 0) {
                area.scale = Math.min(maximalScale, area.scale + scaleFactor)
            } else {
                area.scale = Math.max(minimalScale, area.scale - scaleFactor)
            }
        }
    }

    function calcXY(index) {
        const radius = 1330

        let x = radius * Math.cos(-index / 8 * Math.PI)
        let y = radius * Math.sin(-index / 8 * Math.PI)

        return {x, y}
    }

    function createTrackPiece(sibling, transformation) {
        if (root.trackType === 0) {
            createStraightTrackPiece(sibling, transformation)
        } else if (root.trackType === 1) {
            createCurvedTrackPiece(sibling, transformation)
        } else if (root.trackType === 2) {
            createSwitchTrackPiece(sibling, transformation)
        }
    }

    function createStraightTrackPiece(sibling, transformation) {
        let rotation = (sibling ? sibling.rotation : 0) - 22.5 * transformation.angle
        let x = sibling ? sibling.x : 0
        let y = sibling ? sibling.y : 0

        console.log("sibling: x, y", x, y)

        var component = Qt.createComponent("StraightTrackPiece.qml");
        var sprite = component.createObject(area, {x: x, y: y, rotation: rotation});

        if (transformation.dir > 0) {
            sprite.x -= sprite.height * Math.sin(Math.PI / 8)
            sprite.y -= sprite.height * Math.cos(Math.PI / 8)
            sprite.bottomVisible = false
        } else {
            sprite.y += sibling ? sibling.height : 0
        }

        // sprite.x += transformation.offsetX - sprite.width       // TODO sibling?
        // sprite.y = (sibling ? sibling.y : 0) - sprite.height    // TODO offsetY

        // console.log("after offset: x, y", x, y)

        // sprite.x -= sibling ? 185 : 0
        // sprite.y -= sibling ? -37 : 0
        // console.log("cos, sin",
        //             (Math.cos(Math.PI / 8) * sprite.height).toFixed(1),
        //             (Math.sin(Math.PI / 8)  * sprite.height).toFixed(1))

        // sprite.x -= sibling ? (Math.cos(Math.PI / 8) * sprite.width) : 0
        //sprite.y -= sibling ? (sprite.width - Math.sin(Math.PI / 8)  * sprite.width) : 0

        console.log("sprite", sprite.width, sprite.height, rotation, x, y)
        sprite["add"].connect (function (transformation) {
            createTrackPiece(sprite, transformation)
        })

        sprite.transformOrigin = Item.BottomRight

        // if (sibling) {
        //     if (transformation.angle > 0) {
        //         sprite.y = sibling.y - sprite.height
        //         sprite.bottomVisible = false
        //     } else {
        //         sprite.y = sibling.y + sibling.height
        //         sprite.topVisible = false
        //     }
        // }
    }

    function createSwitchTrackPiece(sibling, transformation) {
        let index = (sibling ? (Math.abs(sibling.rotation) / 22.5) : 0) * transformation.angle
        let rotation = sibling ? sibling.rotation : 0
        let p = calcXY(index)

        var component = Qt.createComponent("SwitchTrackPiece.qml");
        var sprite = component.createObject(area, {x: p.x, y: p.y, rotation: rotation});

        sprite["add"].connect (function (transformation) {
            createTrackPiece(sprite, transformation)
        })

        if (sibling) {
            if (transformation.angle === 1) {
                sprite.y = sibling.y - sprite.height
                sprite.bottomVisible = false
            } else if (transformation.angle === 2 ) {
                sprite.y = sibling.y - sprite.height
                sprite.bottomVisible = false
            } else if (transformation.angle === -1) {
                sprite.y = sibling.y + sibling.height
                sprite.topRightVisible = false
            }
        }
    }

    function createCurvedTrackPiece(sibling, transformation) {
        let index = (sibling ? (Math.abs(sibling.rotation) / 22.5 + 1) : 0) * transformation.angle
        let rotation = index * -22.5
        let p = calcXY(index)

        let component = Qt.createComponent("CurvedTrackPiece.qml");
        let sprite = component.createObject(area, { x: p.x, y: p.y, rotation: rotation });

        // sprite.transformOrigin = Item.BottomRight

        if (sibling) {
            if (rotation < 0) {
                sprite.bottomVisible = false
            } else {
                sprite.topVisible = false
            }
        }

        sprite["add"].connect (function (transformation) {
            createTrackPiece(sprite, transformation)
        })
    }

    Component.onCompleted: root.createTrackPiece(undefined, {angle: 1, offsetX: 0, offsetY: 0})

    Item {
        id: area
        x: 200
        y: 400
        height: parent.height
        width: parent.width
        // scale: 0.7
    }
}
