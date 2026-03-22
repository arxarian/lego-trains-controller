import QtQuick
import QtQuick.Shapes
import TrainView

Item {
    id: root

    property var model
    property color strokeColor: "red"
    property int strokeWidth: 10
    property var _createdElements: []

    function rebuildPath() {
        for (var i = 0; i < root._createdElements.length; i++)
            root._createdElements[i].destroy()
        root._createdElements = []

        var count = root.model ? root.model.rowCount() : 0
        if (count === 0) {
            shapePath.startX = 0
            shapePath.startY = 0
            shapePath.pathElements = []
            return
        }

        var first = root.model.data(root.model.index(0, 0), PathIndicators.Role.ObjectRole)
        shapePath.startX = Qt.binding(function() { return first.x })
        shapePath.startY = Qt.binding(function() { return first.y })

        var elements = []
        for (var i = 1; i < count; i++) {
            var item = root.model.data(root.model.index(i, 0), PathIndicators.Role.ObjectRole)
            var pl = lineComponent.createObject(root, {
                "x": Qt.binding((function(obj) { return function() { return obj.x } })(item)),
                "y": Qt.binding((function(obj) { return function() { return obj.y } })(item))
            })
            elements.push(pl)
        }
        root._createdElements = elements
        shapePath.pathElements = elements
    }

    Shape {
        anchors.fill: parent
        layer.enabled: true
        layer.samples: 4

        ShapePath {
            id: shapePath

            fillColor: "transparent"
            strokeColor: root.strokeColor
            strokeWidth: root.strokeWidth

            capStyle: ShapePath.RoundCap
            joinStyle: ShapePath.RoundJoin

            startX: 0
            startY: 0
        }
    }

    Connections {
        target: root.model
        function onRowsInserted() { root.rebuildPath() }
        function onRowsRemoved() { root.rebuildPath() }
    }

    Component {
        id: lineComponent
        PathLine { }
    }

    Component {
        id: curveComponent
        PathQuad { }
    }
}
