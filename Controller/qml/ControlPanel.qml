import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: root

    readonly property real buttonWidth: 55

    spacing: 0

    Row {
        id: projectButtons

        Button {
            text: "Save"
            onClicked: projectStorage.saveProject(project)
        }

        Button {
            text: "Load"
            onClicked: projectStorage.loadProject(project.name)
        }

        CheckBox {
            text: "Grid"
            checked: Globals.gridVisible
            onClicked: Globals.gridVisible = checked
        }

        CheckBox {
            text: "Track Frame"
            checked: Globals.trackFrameVisible
            onClicked: Globals.trackFrameVisible = checked
        }

        CheckBox {
            text: "Rotation Points"
            checked: Globals.rotationPointsVisible
            onClicked: Globals.rotationPointsVisible = checked
        }
    }

    ButtonGroup { id: group }

    GridLayout {
        columns: 6

        Label {
            text: "Rails"
        }

        Repeater {
            model: railTypes

            Button {
                id: railItem
                property RailType rail: model.object

                checked: Globals.selectedRail === index  // just for the init
                checkable: true
                text: railItem.rail.name
                onClicked: {
                    Globals.selectedMarker = -1
                    Globals.selectedRail = index
                    markerTypes.markersActive = false
                    railTypes.railsActive = true
                }

                ButtonGroup.group: group
                Layout.preferredWidth: root.buttonWidth
            }
        }

        Item {}

        Label {
            text: "Markers"
        }

        Repeater {
            model: markerTypes

            Button {
                id: markerItem
                property MarkerType marker: model.object

                checkable: true
                text: markerItem.marker.name

                onClicked: {
                    Globals.selectedMarker = index
                    Globals.selectedRail = -1
                    markerTypes.markersActive = true
                    railTypes.railsActive = false
                }

                ButtonGroup.group: group
                Layout.preferredWidth: root.buttonWidth
            }
        }
    }
}
