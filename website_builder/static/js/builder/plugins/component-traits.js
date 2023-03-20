const link_toolbar = [
  {
    attributes: {
      class: "fa fa-arrows",
    },
    command: "tlb-move",
  },
  {
    attributes: {
      class: "fa fa-clone",
    },
    command: "tlb-clone",
  },
  {
    attributes: {
      class: "fa fa-trash-o",
    },
    command: "tlb-delete",
  },
  {
    attributes: {
      class: "fa fa-gear",
    },
    command:  (editor) => {
      const selected_link = editor.getSelected()
      const pages = editor.Pages.getAll()
      const content = pages.map((p) => {
       return `<option value="${p.id}">${p.attributes.name}</option>`
      })
      editor.Modal.setTitle("Connect page to link")
      .setContent(`
        <div class"my-2">
          <div class="form-group" >
            <label for="pageSelectForLink" class="mt-2">Select Page</label>
            <select id="saveConnectPageLinkSelect" class="form-control" id="pageSelectForLink">
            ${content}
            </select>
            <button id="saveConnectPageLinkBtn" class="btn btn-primary mt-2"">Save</button>
          </div>
        </div>
      `
      ).open();
      const saveConnectPageLink = document.getElementById("saveConnectPageLinkBtn");
      saveConnectPageLink.addEventListener("click",() => {
        const value = document.getElementById("saveConnectPageLinkSelect").value;
        if (value === "index"){
          selected_link.attributes.attributes.href = "/"
        }else{
          selected_link.attributes.attributes.href = `/${value}`
        }
        
        editor.Modal.close()
      })

    }
  },
];


grapesjs.plugins.add("component-traits", function (editor) {
  editor.DomComponents.addType("link", {
    extend: "link",
    isComponent: (el) => el.tagName == "A",
    model: {
      defaults: {
        toolbar: link_toolbar,
      },
    },
  });

  editor.DomComponents.addType("iframe", {
    isComponent: (el) => el.tagName === "IFRAME",
    model: {
      defaults: {
        type: "iframe",
        traits: [
          {
            type: "text",
            label: "src",
            name: "src",
          },
        ],
      },
    },
  });
  editor.DomComponents.addType("textarea", {
    isComponent: (el) => el.tagName === "TEXTAREA",
    model: {
      defaults: {
        traits: ["name", "placeholder", { type: "checkbox", name: "required" }],
      },
    },
  });
  editor.DomComponents.addType("input", {
    isComponent: (el) => el.tagName == "INPUT",
    model: {
      defaults: {
        traits: [
          // Strings are automatically converted to text types
          "name", // Same as: { type: 'text', name: 'name' }
          "placeholder",
          {
            type: "select", // Type of the trait
            label: "Type", // The label you will see in Settings
            name: "type", // The name of the attribute/property to use on component
            options: [
              { id: "text", name: "Text" },
              { id: "email", name: "Email" },
              { id: "number", name: "Number" },
            ],
          },
          {
            type: "checkbox",
            name: "required",
          },
        ],
        // As by default, traits are binded to attributes, so to define
        // their initial value we can use attributes
        attributes: { type: "text", required: true },
      },
    },
  });
});
