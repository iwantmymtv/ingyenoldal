const swv = 'sw-visibility';
const expt = 'export-template';
const osm = 'open-sm';
const otm = 'open-tm';
const ola = 'open-layers';
const obl = 'open-blocks';
const ful = 'fullscreen';
const prv = 'preview';

const styleManagerConst = {
    sectors: [{
        name: 'General',
        open: false,
        buildProps: ['float', 'display', 'position', 'top', 'right', 'left', 'bottom']
      },{
        name: 'Flex',
        open: false,
        buildProps: ['flex-direction', 'flex-wrap', 'justify-content', 'align-items', 'align-content', 'order', 'flex-basis', 'flex-grow', 'flex-shrink', 'align-self']
      },{
        name: 'Dimension',
        open: false,
        buildProps: ['width', 'height', 'max-width', 'min-height', 'margin', 'padding'],
      },{
        name: 'Typography',
        open: false,
        buildProps: ['font-family', 'font-size', 'font-weight', 'letter-spacing', 'color', 'line-height', 'text-shadow'],
      },{
        name: 'Decorations',
        open: false,
        buildProps: ['border-radius-c', 'background-color', 'border-radius', 'border', 'box-shadow', 'background'],
      },{
        name: 'Extra',
        open: false,
        buildProps: ['transition', 'perspective', 'transform'],
      }
    ]}

const panelConst = {
      defaults: [
        {
          id: 'commands',
          buttons: [{}]
        },
        {
          id: 'options',
          buttons: [
            {
              active: false,
              id: swv,
              className: 'fa fa-square-o',
              command: swv,
              context: swv,
              attributes: { title: 'View components' }
            },
            {
              id: prv,
              className: 'fa fa-eye',
              command: prv,
              context: prv,
              attributes: { title: 'Preview' }
            },
            {
              id: ful,
              className: 'fa fa-arrows-alt',
              command: ful,
              context: ful,
              attributes: { title: 'Fullscreen' }
            },
            {
              id: "save",
              className: 'fa fa-save',
              command (editor) {
                try {
                  const csrf = document.querySelector('[name=csrfmiddlewaretoken]').value;
                  saveProject(editor,csrf)
                  editor.Modal.setTitle('Mentve')
                  .setContent(`
                    <div class="my-2">
                    <p>Szeretnéd befejezni a szerkesztést?</p>
                    <button class="btn btn-primary" onclick="LeaveProject('/my-websites')" >Igen</button>
                    </div>
                  `)
                  .open();
                } catch (error){
                   editor.Modal.setTitle('Error')
                  .setContent(`
                    <div class="my-2">
                    <p>${error}</p>
                    </div>
                  `)
                  .open();
                }
              },
              context:"save",
              attributes: { title: 'Save' }
            },
          ],

        },
        {
          id: 'views',
          buttons: [
            {
              id: osm,
              className: 'fa fa-paint-brush',
              command: osm,
              active: true,
              togglable: 0,
              attributes: { title: 'Open Style Manager' }
            },
            {
              id: otm,
              className: 'fa fa-cog',
              command: otm,
              togglable: 0,
              attributes: { title: 'Settings' }
            },
            {
              id: ola,
              className: 'fa fa-bars',
              command: ola,
              togglable: 0,
              attributes: { title: 'Open Layer Manager' }
            },
            {
              id: obl,
              className: 'fa fa-th-large',
              command: obl,
              togglable: 0,
              attributes: { title: 'Open Blocks' }
            },
          ]
        },

      ],
    }