import QtQuick
import QtQuick.Shapes
import TrainView

Item {
    id: root

    property var model  // TODO - why var and not Connectors?

    Binding {
        target: pathMove
        property: "path"
        value: root.model ? root.model.data(root.model.index(0, 0), PathIndicators.Role.ObjectRole) : null
    }

    Shape {
        anchors.fill: parent
        layer.enabled: true
        layer.samples: 4

        ShapePath {
            id: shapePath

            fillColor: "transparent"
            strokeColor: "red"
            strokeWidth: 10

            capStyle: ShapePath.RoundCap
            joinStyle: ShapePath.RoundJoin

             // Binding to the first element of your model
            PathMove {
                id: pathMove

                property PathIndicator path: null

                x: path ? path.x : 0
                y: path ? path.y : 0
            }
        }

        Instantiator {
            model: root.model

            delegate: Loader {
                property PathIndicator path: model.object

                active: index > 0
                sourceComponent: {
                    return lineComponent
                    //if (model.type === 0) return lineComponent
                    //if (model.type === 1) return curveComponent
                    //return null
                }
            }

            // add generated PathElements into the ShapePath
            onObjectAdded: (index, object) => {
                if (object.item) shapePath.pathElements.push(object.item)
            }
            // handle model changes/removals
            onObjectRemoved: (index, object) => {}
        }

        Component {
            id: lineComponent
            PathLine {
                x: path.x
                y: path.y
            }
        }

        Component {
            id: curveComponent
            PathQuad {
                x: path.x
                y: path.y
                controlX: path.c_x
                controlY: path.c_y
            }
        }
    }
}
