function grape_app(tmpl) {
  const csrf = document.querySelector('[name=csrfmiddlewaretoken]').value;
  const template = tmpl.template;
  let website = null;
  let pages_array = [];

  let template_styles_urls = [];
  let template_styles = "";

  let template_scripts_urls = [];
  let template_scripts = [];

  let index_html_content = "";
  let index_style = "";

  template.styles.map((s) => {
    template_styles_urls.push(s.url_path);
    template_styles += s.style;
  });
  template.scripts.map((s) => {
    template_scripts_urls.push(s.url_path);
    template_scripts.push(s.script);
  });

  if (tmpl.website) {
    website = tmpl.website;
    index_style = `<style>${website.css}</style>`;
    index_html_content = website.html_content;
    pages_array = website.pages;
  } else {
    index_style = `<style>${template_styles}</style>`;
    index_html_content = template.html_content;
    //create pages object
    pages_array = template.pages;
  }

  const editor = grapesjs.init({
    canvas: {
      styles: template_styles_urls,
      scripts: template_scripts_urls,
    },
    pageManager: {
      pages: [
        {
          id: "index",
          name: "Index",
          styles: index_style,
          component: `${index_html_content}`,
        },
      ],
    },
    allowScripts: 1,
    showDevices: 0,
    devicePreviewMode: 1,
    container: "#gjs",
    height: "100%",
    noticeOnUnload: false,
    fromElement: true,
    plugins: ["component-traits", "grapesjs-custom-code"],
    pluginsOpts: {
      "grapesjs-custom-code": {
        blockLabel: "Custom Code",
      },
    },
    assetManager: {
      upload: "/upload/assets",
      uploadName: "assets",
      headers: {
        "X-CSRFToken": csrf,
      },
    },
    storageManager: { type: null },
    panels: panelConst,
    styleManager: styleManagerConst,
  });
  return {
    'editor':editor,
    'pages_array':pages_array
  }
}

