import QtQuick

Item {
    id: root

    readonly property bool selected: root.activeFocus
    property bool propagateComposedEvents: false
    property bool enabled: true

    property var rotateAction: function () {
        console.warn("no rotate action defined")
    }

    property var deleteAction: function () {
        console.warn("no delete action defined")
    }

    z: root.selected ? 10 : 0

    focus: true

    Keys.onPressed: (event)=> {
                        if (event.key === Qt.Key_Delete) {
                            root.deleteAction()
                            event.accepted = true
                        } else if (event.key === Qt.Key_R) {
                            root.rotateAction()
                            event.accepted = true
                        }
                    }

    SelectedMarker {
        anchors.fill: parent
        anchors.margins: -radius / 2
        z: 10
        visible: root.selected
    }

    MouseArea {
        anchors.fill: parent
        enabled: root.enabled
        propagateComposedEvents: root.propagateComposedEvents
        onClicked: function(mouse) {
            mouse.accepted = !propagateComposedEvents
            root.forceActiveFocus()
        }
    }
}
