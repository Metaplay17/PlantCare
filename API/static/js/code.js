document.addEventListener("DOMContentLoaded", async () => {
  window.dispatchEvent(new HashChangeEvent('hashchange'));
  // Добавить вход
});

window.addEventListener('hashchange', async () => {
  let action = window.location.hash.split('#')[1].split("/")[0];
  let subject = window.location.hash.split('#')[1].split("/")[1];

  switch (action) {
    case "Plants":
      await LoadPage("Plants");
        let response = await ServerRequest("GetPlants", {});
        if (response.status === 200) {
          let plants = await response.json();
          renderPlants(plants);
        }
        else {
          document.getElementById("content-block").innerHTML = "<h1>ERROR</h1>";
        }
      break;

    case "AddPlant":
      await LoadPage("AddPlant");
      document.getElementById("add-plant-submit-btn").addEventListener("click", async (event) => {
        event.preventDefault();
        // Получаем значения полей
        let plantName = document.getElementById("plant-name-input").value.trim();
        let plantScienceName = document.getElementById("plant-science-name-input").value.trim();
        let plantPlace = document.getElementById("plant-place-input").value;

        // Проверяем, что обязательные поля заполнены
        if (plantName === "" || plantScienceName === "") {
            document.getElementById("info").innerHTML = "ВВЕДИТЕ ВСЕ ОБЯЗАТЕЛЬНЫЕ ПОЛЯ";
            return;
        }

        // Обработчик для файла
        let plantMainPhoto = null;
        let fileInput = document.getElementById("plant-main-photo-input");

        if (fileInput.files.length > 0) {
            let file = fileInput.files[0];

            // Используем FileReader для чтения файла в Base64
            let reader = new FileReader();

            // Создаем Promise для ожидания завершения чтения файла
            plantMainPhoto = new Promise((resolve, reject) => {
                reader.onload = () => {
                    resolve(reader.result.split(",")[1]); // Убираем префикс "data:image/jpeg;base64,"
                };
                reader.onerror = (error) => {
                    reject(error);
                };
                reader.readAsDataURL(file); // Читаем файл как Data URL
            });
        } else {
            plantMainPhoto = null; // Если файл не выбран
        }
        // Ждем завершения чтения файла (если файл выбран)
        let base64Photo = plantMainPhoto ? await plantMainPhoto : null;

        // Отправляем данные на сервер
        let response = await ServerRequest("AddPlant", {
            "name": plantName,
            "science_name": plantScienceName,
            "place": plantPlace,
            "main_photo": base64Photo, // Файл в Base64 или null
        });

        // Проверяем статус ответа
        if (response.status !== 200) {
            document.getElementById("info").innerHTML = "SERVER ERROR";
        }
      });
      break;

    case "Plant":
      if (subject == "" || subject == null) {
        window.location.hash = "#Plants";
        window.dispatchEvent(new HashChangeEvent('hashchange'));
        break;
      }

      DisplayPlant(subject);
      break;

    case "Photos":
      loadPhotos();
      break;

    case "Photo":
        if (subject == "" || subject == null) {
          window.location.hash = "#Photos";
          window.dispatchEvent(new HashChangeEvent('hashchange'));
          break;
        }

        DisplayPhoto(subject);
        break;
    case "Notes":
      loadNotes();
      break;

    case "Note":
        if (subject == "" || subject == null) {
          window.location.hash = "#Photos";
          window.dispatchEvent(new HashChangeEvent('hashchange'));
          break;
        }

        DisplayNote(subject);
        break;
    }

      

});

async function LoadPage(action) {
  let response = await ServerRequest("GetPage", {"Page": action});
  if (response.status == 200) {
    let html = await response.text();
    document.getElementById("content-block").innerHTML = html;
  }
  else {
    document.getElementById("content-block").innerHTML = "<h1>LOAD PAGE ERROR</h1>";
  }
}

async function ServerRequest(action, actionData) {
  data = {
    "action": action,
    "actionData": actionData
  }
  return await fetch("http://127.0.0.1:5000/", {
        method: 'POST',
        body: JSON.stringify(data),
        headers: {
        'Content-Type': 'application/json; charset=UTF-8'
    }
  });
}

function CheckSQLInput(input) {
  // Примеры ключевых слов и символов, характерных для SQL-инъекций
  const sqlInjectionPattern = /(\b(ALTER|CREATE|DELETE|DROP|EXEC(UTE)?|INSERT( +INTO)?|MERGE|SELECT|UPDATE|UNION( +ALL)?|TRUNCATE|RENAME|REPLACE|LOAD_FILE|OUTFILE|DUMPFILE|BULK +INSERT|GRANT|REVOKE|DENY|DECLARE|FETCH|OPEN|CLOSE|XP_CMDSHELL|SP_OACREATE|WAITFOR +DELAY|BEGIN|END|IF|ELSE|WHILE|CURSOR|PROCEDURE|FUNCTION|TRIGGER|SCHEMA|TABLE|VIEW|INDEX|SEQUENCE|USER|DATABASE|SESSION|TRANSACTION|COMMIT|ROLLBACK|SAVEPOINT|LOCK|UNLOCK|VACUUM|ANALYZE|EXPLAIN|DESCRIBE|SHOW|USE|FROM|WHERE|HAVING|GROUP +BY|ORDER +BY|LIMIT|OFFSET|JOIN|INNER|OUTER|LEFT|RIGHT|FULL|CROSS|NATURAL|USING|ON|AS|CASE|WHEN|THEN|ELSE|END|BETWEEN|LIKE|ILIKE|REGEXP|IN|EXISTS|NOT|NULL|IS|DISTINCT|ANY|ALL|SOME|COLLATE|CAST|CONVERT|NULLIF|COALESCE|IFNULL|NVL)\b|;|--|\/\*|\*\/|@@|@|\$\$|\/\*!.+\*\/|0x[0-9a-fA-F]+|\b(TRUE|FALSE|NULL)\b|\b(AND|OR|XOR|DIV|MOD|BETWEEN|RLIKE|SOUNDS +LIKE|REGEXP +BINARY)\b|\b(CHAR|CONCAT|SUBSTRING|SUBSTR|LENGTH|REPLACE|REVERSE|UPPER|LOWER|TRIM|LTRIM|RTRIM|POSITION|INSTR|LOCATE|LPAD|RPAD|SPACE|REPEAT|HEX|UNHEX|BIN|OCT|ASCII|ORD|CONV|FORMAT|ROUND|CEIL|FLOOR|TRUNCATE|ABS|SIGN|SQRT|POW|POWER|EXP|LOG|LOG10|LN|SIN|COS|TAN|ASIN|ACOS|ATAN|ATAN2|RADIANS|DEGREES|PI|RAND|UUID|MD5|SHA1|SHA2|AES_ENCRYPT|AES_DECRYPT|ENCODE|DECODE|COMPRESS|UNCOMPRESS|CRC32|ENCRYPT|DECRYPT|PASSWORD|OLD_PASSWORD|RANDOM_BYTES|TO_BASE64|FROM_BASE64)\s*\(|\/\*![0-9]{5}|\b(ADDDATE|ADDTIME|CONVERT_TZ|CURDATE|CURRENT_DATE|CURRENT_TIME|CURRENT_TIMESTAMP|CURTIME|DATE|DATEDIFF|DATE_ADD|DATE_FORMAT|DATE_SUB|DAY|DAYNAME|DAYOFMONTH|DAYOFWEEK|DAYOFYEAR|EXTRACT|FROM_DAYS|FROM_UNIXTIME|GET_FORMAT|HOUR|LAST_DAY|LOCALTIME|LOCALTIMESTAMP|MAKEDATE|MAKETIME|MICROSECOND|MINUTE|MONTH|MONTHNAME|NOW|PERIOD_ADD|PERIOD_DIFF|QUARTER|SECOND|SEC_TO_TIME|STR_TO_DATE|SUBDATE|SUBTIME|SYSDATE|TIME|TIMEDIFF|TIMESTAMP|TIMESTAMPADD|TIMESTAMPDIFF|TIME_FORMAT|TIME_TO_SEC|TO_DAYS|TO_SECONDS|UNIX_TIMESTAMP|UTC_DATE|UTC_TIME|UTC_TIMESTAMP|WEEK|WEEKDAY|WEEKOFYEAR|YEAR|YEARWEEK)\s*\(|\b(IF|ELSE|CASE|WHEN|THEN|END|NULLIF|COALESCE|GREATEST|LEAST|BIN_TO_UUID|UUID_TO_BIN|JSON_ARRAY|JSON_ARRAYAGG|JSON_OBJECT|JSON_OBJECTAGG|JSON_QUOTE|JSON_UNQUOTE|JSON_CONTAINS|JSON_CONTAINS_PATH|JSON_EXTRACT|JSON_KEYS|JSON_OVERLAPS|JSON_SEARCH|JSON_VALUE|JSON_ARRAY_APPEND|JSON_ARRAY_INSERT|JSON_INSERT|JSON_MERGE|JSON_MERGE_PATCH|JSON_MERGE_PRESERVE|JSON_REMOVE|JSON_REPLACE|JSON_SET|JSON_DEPTH|JSON_LENGTH|JSON_TYPE|JSON_VALID|JSON_TABLE|JSON_SCHEMA_VALID|JSON_SCHEMA_VALIDATION_REPORT|JSON_PRETTY|JSON_STORAGE_SIZE|JSON_STORAGE_FREE|JSON_ARRAYAGG|JSON_OBJECTAGG)\s*\(|\b(GEOMETRY|POINT|LINESTRING|POLYGON|MULTIPOINT|MULTILINESTRING|MULTIPOLYGON|GEOMETRYCOLLECTION|ST_ASBINARY|ST_ASTEXT|ST_BUFFER|ST_CENTROID|ST_CONTAINS|ST_CONVEXHULL|ST_CROSSES|ST_DIFFERENCE|ST_DIMENSION|ST_DISJOINT|ST_DISTANCE|ST_ENDPOINT|ST_ENVELOPE|ST_EQUALS|ST_EXTERIORRING|ST_GEOHASH|ST_GEOMETRYTYPE|ST_INTERIORRINGN|ST_INTERSECTION|ST_INTERSECTS|ST_ISCLOSED|ST_ISEMPTY|ST_ISSIMPLE|ST_LENGTH|ST_NUMGEOMETRIES|ST_NUMINTERIORRING|ST_NUMPOINTS|ST_OVERLAPS|ST_POINTN|ST_SIMPLIFY|ST_STARTPOINT|ST_SYMDIFFERENCE|ST_TOUCHES|ST_UNION|ST_WITHIN|ST_X|ST_Y)\s*\()/gi;

  if (sqlInjectionPattern.test(input)) {
      return false;
  }
  return true;
}

function formatDate(inputDateStr) {
  const date = new Date(inputDateStr);

  // Проверяем, что дата корректна
  if (isNaN(date.getTime())) {
      throw new Error("Некорректная дата");
  }

  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0'); // Месяцы начинаются с 0
  const year = date.getFullYear();

  return `${day}.${month}.${year}`;
}

function formatDateForInput(inputDateStr) {
  const date = new Date(inputDateStr);

  // Проверяем, что дата корректна
  if (isNaN(date.getTime())) {
      throw new Error("Некорректная дата");
  }

  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0'); // Месяцы начинаются с 0
  const year = date.getFullYear();

  return `${year}-${month}-${day}`;
}


function renderPlants(data) {
  const contentArea = document.getElementById('content-area');
  contentArea.innerHTML = ''; // Очистка перед добавлением новых данных

  if (!Array.isArray(data) || data.length === 0) {
      contentArea.innerHTML = '<p>Нет доступных растений</p>';
      return;
  }

  data.forEach(plant => {
      // Создаем элемент карточки
      const card = document.createElement('div');
      card.className = 'plant-card';

      // Фотография
      const img = document.createElement('img');
      img.className = 'plant-photo';
      img.alt = plant.name;

      // Если фото есть — устанавливаем base64, иначе ставим заглушку
      if (plant.main_photo) {
          img.src = `data:image/jpeg;base64,${plant.main_photo}`;
      } else {
          img.src = 'https://via.placeholder.com/300x200?text=No+Photo';
      }

      // Информация
      const info = document.createElement('div');
      info.className = 'plant-info';

      const name = document.createElement('h3');
      name.className = 'plant-name';
      name.textContent = plant.name;

      const sciName = document.createElement('p');
      sciName.className = 'plant-scientific';
      sciName.textContent = plant.science_name || 'Научное название не указано';

      const meta = document.createElement('p');
      meta.className = 'plant-meta';
      meta.textContent = `Добавлено: ${formatDate(plant.date_added)} | Место: ${Math.round(plant.place)}`;

      // Сборка карточки
      info.appendChild(name);
      info.appendChild(sciName);
      info.appendChild(meta);

      card.appendChild(img);
      card.appendChild(info);

      // Добавляем в контейнер
      contentArea.appendChild(card);

      card.addEventListener("click", () => {
        window.location.hash = `#Plant/${plant.plant_id}`;
        window.dispatchEvent(new HashChangeEvent('hashchange'));
      });
  });
}

async function DisplayPlant(plant_id) {
  await LoadPage("Plant");
  let plantInfo = await ServerRequest("Plant", {"plant_id": plant_id});
  plantInfo = await plantInfo.json();
  document.getElementById("plant-name").value = plantInfo.name;
  document.getElementById("plant-science-name").value = plantInfo.science_name;
  document.getElementById("plant-place").value = Math.floor(plantInfo.place);
  document.getElementById("image-block").innerHTML = `<img src=data:image/jpeg;base64,${plantInfo.main_photo}>`

  async function savePlantHandler() {
    if (
      document.getElementById("plant-name").value == "" ||
      document.getElementById("plant-science-name").value == "" ||
      document.getElementById("plant-place").value == ""
    ) {
      document.getElementById("info").innerHTML = "ЗАПОЛНИТЕ ВСЕ ПОЛЯ";
      return;
    }

    const response = await ServerRequest("UpdatePlant", {
      "plant_id": plant_id,
      "plant_name": document.getElementById("plant-name").value,
      "plant_science_name": document.getElementById("plant-science-name").value,
      "plant_place": document.getElementById("plant-place").value
    });

    if (response.status === 200) {
      return;
    } else {
      document.getElementById("info").innerHTML = `ERROR: ${response.status}`;
    }
  }

  // Перед добавлением — удалим старый обработчик
  const saveBtn = document.getElementById("save-btn");
  saveBtn.removeEventListener("click", savePlantHandler);
  saveBtn.addEventListener("click", savePlantHandler);
  }

async function loadPhotos() {
    await LoadPage("Photos");
    const container = document.querySelector('.photos-container');

    try {
        // Заменить на свой URL API
        const response = await ServerRequest("GetPhotos", {}); // Примерный путь
        const photoData = await response.json(); // Получаем массив строк base64

        // Очистка контейнера перед заполнением
        container.innerHTML = '';

        // Добавление фото в DOM
        photoData.forEach(photo => {
            const card = document.createElement('div');
            card.classList.add('photo-card');

            const img = document.createElement('img');
            img.src = `data:image/jpeg;base64,${photo.image}`; // присваиваем напрямую, т.к. это data URL
            img.alt = 'Plant photo';

            img.addEventListener("click", () => {
              window.location.hash = `#Photo/${photo.photo_id}`;
              window.dispatchEvent(new HashChangeEvent('hashchange'));
            });

            card.appendChild(img);
            container.appendChild(card);
        });
    } catch (error) {
        console.error('Ошибка при загрузке фотографий:', error);
        container.innerHTML = '<p>Не удалось загрузить фотографии</p>';
    }
}

async function DisplayPhoto(photo_id) {
    await LoadPage("Photo");
    
    let photoInfo = await ServerRequest("Photo", {"photo_id": photo_id});
    photoInfo = await photoInfo.json();
    let plants = await ServerRequest("GetPlants", {});
    plants = await plants.json();
    const selector = document.getElementById("plant-select");
    let plant_id = await ServerRequest("PlantIdByPhoto", {"photo_id": photo_id});
    plant_id = await plant_id.json();
    plant_id = plant_id["plant_id"];
    let checkbox = document.getElementById("is-main-photo-checkbox");


    let resp = await ServerRequest("IsMainPhoto", {"plant_id": plant_id, "photo_id": photo_id});
    let json = await resp.json();
    if (resp.status != 200) {
        alert(`ERROR: ${json["status"]}`);
    }
    else {
        checkbox.checked = json["isMainPhoto"];
    }


    plants.forEach(plant => {
      selector.innerHTML += `<option value="${plant.plant_id}">${plant.name}</option>\n`;
    });
    selector.value = plant_id;
    document.getElementById("photo-block").innerHTML = `<img class="image" id="image" src=data:image/jpeg;base64,${photoInfo.image}>`;
    document.getElementById("delete-btn").addEventListener("click", async () => {
      let resp = await ServerRequest("DeletePhoto", {"photo_id": photo_id});
      if (resp.status == 200) {
        window.location.hash = "#Photos";
        window.dispatchEvent(new HashChangeEvent('hashchange'));
      }
      else {
        alert(`ERROR: ${resp.status}`);
      }
    });


    // Удаляем предыдущий обработчик, если он существует
    if (checkbox.changeHandler) {
        checkbox.removeEventListener("change", checkbox.changeHandler);
    }

    // Добавляем новый обработчик
    checkbox.changeHandler = async () => {
        let resp = await ServerRequest("ChangeMainPhoto", {"plant_id": selector.value, "photo_id": photo_id, "selected": checkbox.checked});
        let json = await resp.json();
        if (resp.status != 200) {
            alert(`ERROR: ${json["status"]}`);
        }
    };

    checkbox.addEventListener("change", checkbox.changeHandler);


        // Удаляем предыдущий обработчик, если он существует
    if (selector.changeHandler) {
        selector.removeEventListener("change", selector.changeHandler);
    }

    // Добавляем новый обработчик
    selector.changeHandler = async () => {
        let resp = await ServerRequest("IsMainPhoto", {"plant_id": selector.value, "photo_id": photo_id});
        let json = await resp.json();
        if (resp.status != 200) {
            alert(`ERROR: ${json["status"]}`);
        }
        else {
            checkbox.checked = json["isMainPhoto"];
        }
        resp = await ServerRequest("ChangePlantPhoto", {"plant_id": selector.value, "photo_id": photo_id});
        json = await resp.json();
        if (resp.status != 200) {
            alert(`ERROR: ${json["status"]}`);
        }
    };

    selector.addEventListener("change", selector.changeHandler);
  }

async function loadNotes() {
    await LoadPage("Notes");
    const container = document.querySelector('.notes-container');

    try {
        const response = await ServerRequest("GetNotes");
        const notes = await response.json(); // предполагается массив объектов

        if (notes.length > 0) {
            container.innerHTML = '';
        }

        notes.forEach(note => {
          let desc;
            if (note.description.length > 70) {
              desc = note.description.substring(0, 70) + "...";
            }
            else {
              desc = note.description;
            }
            const card = document.createElement('div');
            card.className = 'note-card';

            card.innerHTML = `
                <div class="note-image">
                    <img src="data:image/jpeg;base64,${note.image}" alt="Фото заметки">
                </div>
                <div class="note-content">
                    <h3 class="note-title">${note.note_name}</h3>
                    <p class="note-description">${desc}</p>
                    <p class="note-date">${formatDate(note.date)}</p>
                </div>
            `;

            card.addEventListener("click", () => {
              window.location.hash = `#Note/${note.note_id}`;
              window.dispatchEvent(new HashChangeEvent('hashchange'));
            });

            container.appendChild(card);
        });
    } catch (error) {
        console.error('Ошибка при загрузке заметок:', error);
        container.innerHTML = '<p>Не удалось загрузить заметки</p>';
    }
}

async function DisplayNote(note_id) {
  await LoadPage("Note");

  let noteInfo = await ServerRequest("Note", {"note_id": note_id});
  noteInfo = await noteInfo.json();
  const nameInput = document.getElementById("note-name");
  const descriptionInput = document.getElementById("note-description");
  const dateInput = document.getElementById("note-date");
  let imageBlock = document.getElementById("note-photo-block");

  nameInput.value = noteInfo.name;
  descriptionInput.value = noteInfo.description;
  dateInput.value = formatDateForInput(noteInfo.date_added);
  imageBlock.innerHTML = `<img src=data:image/jpeg;base64,${noteInfo.image}>`;

  async function saveNoteHandler() {
    if (
      document.getElementById("note-name").value == "" ||
      document.getElementById("note-description").value == ""
    ) {
      alert("ЗАПОЛНИТЕ ВСЕ ПОЛЯ");
      return;
    }

    const response = await ServerRequest("UpdateNote", {
      "note_id": note_id,
      "name": document.getElementById("note-name").value,
      "description": document.getElementById("note-description").value,
    });

    if (response.status === 200) {
      return;
    } else {
      alert(`ERROR: ${response.status}`);
    }
  }

  const saveBtn = document.getElementById("save-note-btn");
  saveBtn.removeEventListener("click", saveNoteHandler);
  saveBtn.addEventListener("click", saveNoteHandler);
}



