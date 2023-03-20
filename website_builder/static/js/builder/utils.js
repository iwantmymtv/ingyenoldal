  async function fetchTemplates(id) {
    const response = await fetch(`/templates/api/v1/template/${id}`);
    // waits until the request completes...
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    let data =  response.json();
    return data;
  }

  async function fetchUserAssets() {
    const response = await fetch(`/templates/api/v1/user-assets`);
    // waits until the request completes...
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    let data =  response.json();
    return data;
  } 

  async function saveProject(editor, csrftoken){
    const gjs_div = document.getElementById("gjs");
    const pageManager = editor.Pages
    //get selected to reselect later
    const current = pageManager.getSelected()
    //select main first
    pageManager.select(pageManager.getMain())

    let data = {
      "html_content" : editor.getHtml(),
      "css": editor.getCss(),
      "extra_pages":[]
    }

    if (gjs_div.getAttribute("data-uid")){
      data["website_id"] = gjs_div.getAttribute("data-uid")
    }
    if (gjs_div.getAttribute("data-template-id")){
      data["template_id"] = gjs_div.getAttribute("data-template-id")
    }


    let htmlList = []
    const pg = pageManager.getAll()
    for (i = 1; i < pg.length; i++){
      pageManager.select(pg[i])
      htmlList.push({
        'page_id':pg[i].id,
        'name':pg[i].attributes.name,
        'html_content':editor.getHtml(),
        "css": editor.getCss()
      })
    }
    pageManager.select(current)
    
    data["extra_pages"] = htmlList

    const rawResponse =  await fetch('/save-website/', {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
        "X-CSRFToken": csrftoken,
      },
      body: JSON.stringify(data),
    });
    const content = await rawResponse.json();
    console.log(content)
    gjs_div.setAttribute("data-uid",content.uid)
  };

  const LeaveProject = redirect_url => {
    window.location = redirect_url
  }

  function randomString(len) {
    var p = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";
    return [...Array(len)].reduce(a=>a+p[~~(Math.random()*p.length)],'');
  }

  function slugify(text) {
    text = text.toString().toLowerCase().trim();
  
    const sets = [
      {to: 'a', from: '[ÀÁÂÃÄÅÆĀĂĄẠẢẤẦẨẪẬẮẰẲẴẶἀ]'},
      {to: 'c', from: '[ÇĆĈČ]'},
      {to: 'd', from: '[ÐĎĐÞ]'},
      {to: 'e', from: '[ÈÉÊËĒĔĖĘĚẸẺẼẾỀỂỄỆ]'},
      {to: 'g', from: '[ĜĞĢǴ]'},
      {to: 'h', from: '[ĤḦ]'},
      {to: 'i', from: '[ÌÍÎÏĨĪĮİỈỊ]'},
      {to: 'j', from: '[Ĵ]'},
      {to: 'ij', from: '[Ĳ]'},
      {to: 'k', from: '[Ķ]'},
      {to: 'l', from: '[ĹĻĽŁ]'},
      {to: 'm', from: '[Ḿ]'},
      {to: 'n', from: '[ÑŃŅŇ]'},
      {to: 'o', from: '[ÒÓÔÕÖØŌŎŐỌỎỐỒỔỖỘỚỜỞỠỢǪǬƠ]'},
      {to: 'oe', from: '[Œ]'},
      {to: 'p', from: '[ṕ]'},
      {to: 'r', from: '[ŔŖŘ]'},
      {to: 's', from: '[ßŚŜŞŠȘ]'},
      {to: 't', from: '[ŢŤ]'},
      {to: 'u', from: '[ÙÚÛÜŨŪŬŮŰŲỤỦỨỪỬỮỰƯ]'},
      {to: 'w', from: '[ẂŴẀẄ]'},
      {to: 'x', from: '[ẍ]'},
      {to: 'y', from: '[ÝŶŸỲỴỶỸ]'},
      {to: 'z', from: '[ŹŻŽ]'},
      {to: '-', from: '[·/_,:;\']'}
    ];
  
    sets.forEach(set => {
      text = text.replace(new RegExp(set.from,'gi'), set.to)
    });
  
    return text
      .replace(/\s+/g, '-')    // Replace spaces with -
      .replace(/[^-a-zа-я\u0370-\u03ff\u1f00-\u1fff]+/g, '') // Remove all non-word chars
      .replace(/--+/g, '-')    // Replace multiple - with single -
      .replace(/^-+/, '')      // Trim - from start of text
      .replace(/-+$/, '')      // Trim - from end of text
  }

  function checkIfPageAlreadyExists(pageManager,id){
    const pages = pageManager.getAll()
    let exists = false
    pages.map((p) => {
        if (id === p.id){
          exists = true
        }
      }
    )
    return exists
  }

  function addPanels(panels) {
    panels.addPanel({ id: "devices-c" })
    .get("buttons")
    .add([
      {
        id: "toggle-pages",
        command: function () {
          const pages = document.getElementById("pagesSide");
          pages.classList.toggle("d-none");
        },
        className: "fa fa-bars",
        active: 0,
      },
      {
        id: "set-device-desktop",
        command: function (e) {
          return e.setDevice("Desktop");
        },
        className: "fa fa-desktop",
        active: 1,
      },
      {
        id: "set-device-tablet",
        command: function (e) {
          return e.setDevice("Tablet");
        },
        className: "fa fa-tablet",
      },
      {
        id: "set-device-mobile",
        command: function (e) {
          return e.setDevice("Mobile portrait");
        },
        className: "fa fa-mobile",
      },
    ]);
  panels.render();
  }

  function collapseBlockMenu(editor){
    //collapse blocks menus
    const pn = editor.Panels;
    const bm = editor.Blocks;
    const openBl = pn.getButton("views", "open-blocks");
    editor.on("load", () => {
      openBl && openBl.set("active", 1);
      bm.getCategories().forEach((c) => c.set("open", 0));
    });
  }

  function addBlocks(blocks,blockManager){
    blocks.map((b) => {
      blockManager.add(b.uid, {
        label: b.image_thumbnail
          ? `<img class="w-100" src="${b.image_thumbnail}" alt="${b.name}">`
          : b.name,
        category: b.category.name,
        editable: true,
        content: b.html_content,
      });
    });

  }
  
  function addLiToUl(id,name,is_index=false){
    const pagesUl = document.getElementById("pagesSide");
    if (is_index){
      pagesUl.innerHTML += `
      <li data-page-id="${id}" class=" active cursor-pointer m-1 p-1 list-group-item d-flex justify-content-between align-items-center">
      ${name}  
      <span>
      <i class="fa fa-clone page-clone cursor-pointer"></i>
      </span>
      </li>
      `;
    }else{
      pagesUl.innerHTML += `
      <li data-page-id="${id}" class="cursor-pointer row m-1 p-1 list-group-item d-flex justify-content-between align-items-center">
       <span class="col-12 col-lg-6 p-0">${name}</span> 
      <span class="col-12 col-lg-6 p-0 d-lg-flex justify-content-end">
          <i class="fa fa-clone page-clone cursor-pointer pr-1"></i>
          <i class="fa fa-pencil page-edit cursor-pointer pr-1"></i>
          <i class="fa fa-trash page-trash cursor-pointer"></i>
        </span>
      </li>
      `;
    }
;
  }

  function removePageLiFromUl(id){
    const page_li = document.querySelector(`li[data-page-id=${id}]`);
    page_li.remove()    
  }

  function addExtraPages(pageManager,pages_array){
    //add extrapages to editor
    for (i = 0; i < pages_array.length; i++) {
      pageManager.add(pages_array[i]);
    }
    //add pages li to ui
    const allPages = pageManager.getAll();
    allPages.map((p,i) => {
      if (i === 0){
        addLiToUl(p.id,p.attributes.name,true)
      }else{
        addLiToUl(p.id,p.attributes.name)
      }
    });
  }

  function selectAndaddActiveClassToPageLiOnClick(pageManager){
   //add active class to pgae
    const page_li = document.querySelectorAll("li[data-page-id]");
    page_li.forEach((li) =>
      li.addEventListener("click", (e) => {
        const id = li.dataset.pageId;
        //remove active class
        for (var i = 0; i < page_li.length; i++) {
          page_li[i].classList.remove("active");
        }
        li.classList.add("active");
        pageManager.select(id);
      })
    );
  }

  function startEventListeners(editor){
    const pageManager = editor.Pages
    const modal = editor.Modal

    selectAndaddActiveClassToPageLiOnClick(pageManager)
    addNewPageBtnClick(editor)
    removePage(modal, pageManager);
    editPage(modal, pageManager);  
    clonePage(editor)
  }

  function addNewPage(editor,name,style=null,component=null){
    if (name === ""){
      alert("Name can't be empty ")
      return 
    }
    if (editor.Pages.getAll().length >= editor.max_pages){
      alert(`Maximum ${editor.max_pages} pages`)
      return 
    }
    editor.Pages.add({
        id: slugify(name),
        name: name,
        style: style ? style : null,
        component: component ? component : `<div>New Page</div>`,
    })
    addLiToUl(slugify(name),name)
    startEventListeners(editor)
  }

  function addNewPageBtnClick(editor){
    const addNewPageBtn = document.getElementById("addNewPage");
    addNewPageBtn.addEventListener("click", () => {
      editor.Modal.setTitle("Add new page")
        .setContent(`
          <div class="my-2">
            <div class="form-group">
              <label for="addPageNameInput">Page Name</label>
              <input type="text" required name="name" class="form-control" id="addPageNameInput" aria-describedby="Page name">
              <small id="nameHelp" class="form-text text-muted">Type the name of the page</small>
            </div>
            <button id="addNewPageButton"class="btn btn-primary" type="button" >Add page</button>
          </div>
        `
        ).open();
        const addNewPageButton = document.getElementById("addNewPageButton");
        addNewPageButton.addEventListener("click", (e) => {
          const name = document.getElementById("addPageNameInput").value;
       
          if (checkIfPageAlreadyExists(editor.Pages,slugify(name))){
            alert("Page with this name already exists!")
          }else{
            addNewPage(editor,name)
            editor.Modal.close()
          }         
        })
   
    });
  }

  function removePage(modal,pageManager){
    const page_trashList = document.querySelectorAll("i.page-trash");
    page_trashList.forEach((i) =>
      i.addEventListener("click", (e) => {
        const li = i.parentElement.parentElement;
        const id = li.dataset.pageId;

        modal.setTitle("Add new page")
          .setContent(
            `
              <div class="my-2">
                <p>Do you want to delete this page?</p>
                <button id="removePageButton" class="btn btn-primary" >Yes</button>
              </div>
            `
          )
          .open();

        const removePageButton = document.getElementById("removePageButton");
        removePageButton.addEventListener("click", () => {
          removePageLiFromUl(id);
          pageManager.remove(id);
          modal.close();
        });
      })
    );
  }

  function editPage(modal,pageManager){
    const pageEditList = document.querySelectorAll("i.page-edit");
    pageEditList.forEach((i) =>
      i.addEventListener("click", (e) => {
        const li = i.parentElement.parentElement;
        const id = li.dataset.pageId;

        modal.setTitle("Edit page")
          .setContent(
            `
              <div class="my-2">
              <label for="editPageNameInput">Page Name</label>
              <input value=${li.textContent} type="text" required name="name" class="form-control" id="editPageNameInput" aria-describedby="Page name">
              <small id="emailHelp" class="form-text text-muted">Name of the page</small>
              <button id="editPageButton" class="btn btn-primary mt-2" >Edit Page</button>
              </div>
            `
          )
          .open();

        const editPageButton = document.getElementById("editPageButton");
        editPageButton.addEventListener("click", () => {
          const page = pageManager.get(id)
          const nameInput = document.getElementById("editPageNameInput").value;
          if (nameInput === ""){
            alert("Name can't be empty ")
            return 
          }
          if (checkIfPageAlreadyExists(pageManager,slugify(nameInput))){
            alert("Page with this id already exists!")
          }else{

            page.id = slugify(nameInput)
            page.attributes.id = slugify(nameInput)
            page.attributes.name = nameInput
  
            li.childNodes[1].innerText = nameInput
            li.dataset.pageId = slugify(nameInput)
            modal.close();
          }
     
        });
      })
    );
  }

  function clonePage(editor){
    const pageManager = editor.Pages

    const page_trashList = document.querySelectorAll("i.page-clone");
    page_trashList.forEach((i) =>
      i.addEventListener("click", (e) => {
        const li = i.parentElement.parentElement;
        const id = li.dataset.pageId;
        const page = pageManager.get(id)
        const name = `${page.attributes.name}_${randomString(5)}`
        addNewPage(editor,name,editor.getCss(),editor.getHtml())

      })
    );
  }