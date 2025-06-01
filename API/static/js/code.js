let plants;
let selector;
let resp;

document.addEventListener("DOMContentLoaded", async () => {
  window.dispatchEvent(new HashChangeEvent('hashchange'));
  // Добавить вход

  window.addEventListener('hashchange', async () => {
  let action = window.location.hash.split('#')[1].split("/")[0];
  let subject = window.location.hash.split('#')[1].split("/")[1];

  switch (action) {
    case "Plants":
      await LoadPage("Plants");
      const searchInput = document.getElementById("search-input");
      const searchBtn = document.getElementById("search-btn");
      searchBtn.addEventListener("click", async () => {
        let searchString = searchInput.value;
        if (searchString == '') {
          alert("Введите название");
          return;
        }
        let newData = await ServerRequest("GetFilteredPlants", {"name": searchString.toLowerCase()});
        newData = await newData.json();
        renderPlants(newData);
      });

      searchInput.addEventListener("keypress", (event) => {
        if (event.key == "Enter") {
          searchBtn.click();
        }
      });
      let response = await ServerRequest("GetPlants", {});
      if (response.status === 200) {
        let plants = await response.json();

        const sortingSelector = document.getElementById("sorting-select");
        let sortingType = sortingSelector.value;
        switch (sortingType) {
          case "date-asc":
            plants.sort((a, b) => new Date(a.date_added) - new Date(b.date_added));
            break;
          case "date-desc":
            plants.sort((a, b) => new Date(b.date_added) - new Date(a.date_added));
            break;
          case "place-asc":
            plants.sort((a, b) => a.place - b.place);
            break;
          case "place-desc":
            plants.sort((a, b) => b.place - a.place);
            break;
        }
        renderPlants(plants);

        sortingSelector.addEventListener("change", () => {
          let sortingType = sortingSelector.value;
          switch (sortingType) {
            case "date-asc":
              plants.sort((a, b) => new Date(a.date_added) - new Date(b.date_added));
              break;
            case "date-desc":
              plants.sort((a, b) => new Date(b.date_added) - new Date(a.date_added));
              break;
            case "place-asc":
              plants.sort((a, b) => a.place - b.place);
              break;
            case "place-desc":
              plants.sort((a, b) => b.place - a.place);
              break;
          }
          renderPlants(plants);
        });
      }
      else {
        alert("ERROR");
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

    case "AddNote":
      await LoadPage("AddNote");
      plants = await ServerRequest("GetPlants", {});
      plants = await plants.json();
      selector = document.getElementById("plant-select");
      plants.forEach(plant => {
        selector.innerHTML += `<option value="${plant.plant_id}">${plant.name}</option>\n`;
      });
      document.getElementById("add-note-submit-btn").addEventListener("click", async (event) => {
        event.preventDefault()
        let noteName = document.getElementById("note-name-input").value.trim();
        let noteDescription = document.getElementById("note-description-input").value.trim();
        let plant_id = selector.value;
        let noteDate = document.getElementById("note-date-input").value;

        if (noteName == "" || noteDescription == "" || plant_id == null) {
          alert("Заполните все поля!");
          return;
        }

        // Обработчик для файла
        let notePhoto = null;
        let fileInput = document.getElementById("note-photo-input");

        if (fileInput.files.length > 0) {
            let file = fileInput.files[0];

            // Используем FileReader для чтения файла в Base64
            let reader = new FileReader();

            // Создаем Promise для ожидания завершения чтения файла
            notePhoto = new Promise((resolve, reject) => {
                reader.onload = () => {
                    resolve(reader.result.split(",")[1]); // Убираем префикс "data:image/jpeg;base64,"
                };
                reader.onerror = (error) => {
                    reject(error);
                };
                reader.readAsDataURL(file); // Читаем файл как Data URL
            });
        } else {
            notePhoto = null; // Если файл не выбран
        }
        // Ждем завершения чтения файла (если файл выбран)
        let base64Photo = notePhoto ? await notePhoto : null;

        // Отправляем данные на сервер
        let response = await ServerRequest("AddNote", {
            "name": noteName,
            "description": noteDescription,
            "plant_id": plant_id,
            "image": base64Photo, // Файл в Base64 или null
            "date": noteDate
        });

        // Проверяем статус ответа
        if (response.status !== 200) {
            alert("SERVER ERROR");
        }
        else {
          window.location.hash = "#Notes";
        }
      });
      break;

    case "AddTask":
      await LoadPage("AddTask");
      let plants3 = await ServerRequest("GetPlants", {});
      plants3 = await plants3.json();
      let selector3 = document.getElementById("plant-select");
      plants3.forEach(plant => {
        selector3.innerHTML += `<option value="${plant.plant_id}">${plant.name}</option>\n`;
      });

      let typeSelector = document.getElementById("task-type-select");
      let frequencySelector = document.getElementById("frequency-select");

      let resp1 = await ServerRequest("GetTaskTypes", {});
      let taskTypes1 = await resp1.json()
      resp1 = await ServerRequest("GetRepeatTypes", {});
      let repeatTypes1 = await resp1.json();

      taskTypes1.forEach(type => {
        typeSelector.innerHTML += `<option value="${type.task_type_id}">${type.task_type_description}</option>\n`;
      });

      repeatTypes1.forEach(type => {
        frequencySelector.innerHTML += `<option value="${type.repeat_type_id}">${type.repeat_type_description}</option>\n`;
      });

      document.getElementById("add-task-submit-btn").addEventListener("click", async (event) => {
        event.preventDefault()
        let taskName = document.getElementById("task-name-input").value.trim();
        let taskDescription = document.getElementById("task-description-input").value.trim();
        let plant_id = selector3.value;
        let taskDate = document.getElementById("task-date-input").value;
        let taskTypeId = typeSelector.value;
        let frequencyId = frequencySelector.value;

        if (taskName == "" || taskDescription == "" || plant_id == null || taskTypeId == null || frequencyId == null) {
          alert("Заполните все поля!");
          return;
        }

        // Отправляем данные на сервер
        let response = await ServerRequest("AddTask", {
            "name": taskName,
            "description": taskDescription,
            "plant_id": plant_id,
            "date": taskDate,
            "task_type_id": taskTypeId,
            "frequency_id": frequencyId
        });

        // Проверяем статус ответа
        if (response.status !== 200) {
            alert("SERVER ERROR");
        }
        else {
          window.location.hash = "#Tasks";
        }
      });
      break;

    case "Plant":
      if (subject == "" || subject == null) {
        window.location.hash = "#Plants";
        //window.dispatchEvent(new HashChangeEvent('hashchange'));
        break;
      }

      DisplayPlant(subject);
      break;

    case "Photos":
      await LoadPage("Photos");
      
      let plants1 = await ServerRequest("GetPlants", {});
      plants1 = await plants1.json();
      let selector1 = document.getElementById("plant-select");
      plants1.forEach(plant => {
        selector1.innerHTML += `<option value="${plant.plant_id}">${plant.name}</option>\n`;
      });
      // Удаляем предыдущий обработчик, если он существует
      if (selector1.changeHandler) {
          selector1.removeEventListener("change", selector1.changeHandler);
      }

      // Добавляем новый обработчик
      selector1.changeHandler = async () => {
          let resp = await ServerRequest("GetFilteredPhotos", {"plant_id": selector1.value});
          let json = await resp.json();
          if (resp.status != 200) {
              alert(`ERROR: ${json["status"]}`);
          }
          else {
            loadPhotos(json);
          }
      };
      selector1.addEventListener("change", selector1.changeHandler);

      const uploadBtn = document.getElementById("upload-btn");
      const fileInput = document.getElementById("file-input");
      uploadBtn.addEventListener("click", () => {
        fileInput.click();
      });

      fileInput.addEventListener("change", (event) => {
        const file = event.target.files[0];

        // Читаем файл как Base64
        const reader = new FileReader();
        reader.onload = async (e) => {
            const base64String = e.target.result;

            // Отправляем Base64 на сервер
            let response = await ServerRequest("AddPhotoWithoutPlant", {
              "image": base64String
            });
          };

        reader.readAsDataURL(file); // Читаем файл как Data URL (Base64)
      });

      const resp = await ServerRequest("GetPhotos", {});
      const photoData = await resp.json();
      loadPhotos(photoData);
      break;

    case "Photo":
        if (subject == "" || subject == null) {
          window.location.hash = "#Photos";
          //window.dispatchEvent(new HashChangeEvent('hashchange'));
          break;
        }

        DisplayPhoto(subject);
        break;
    case "Notes":
      await LoadPage("Notes");
      let respNotes = await ServerRequest("GetNotes");
      let defNotes = await respNotes.json();
      loadNotes(defNotes);

      const searchNoteInput = document.getElementById("search-input");
      searchNoteInput.addEventListener("input", async () => {
        let notes1 = defNotes.filter(note => note.note_name.toLowerCase().includes(searchNoteInput.value.toLowerCase()));
        loadNotes(notes1);
      });
      break;

    case "Note":
        if (subject == "" || subject == null) {
          window.location.hash = "#Tasks";
          //window.dispatchEvent(new HashChangeEvent('hashchange'));
          break;
        }

        DisplayNote(subject);
        break;

    case "Tasks":
        let tasks1 = await ServerRequest("GetTasks", {});
        tasks1 = await tasks1.json(); 
        loadTasks(tasks1);
        break;

    case "Task":
        if (subject == "" || subject == null) {
          window.location.hash = "#Tasks";
          //window.dispatchEvent(new HashChangeEvent('hashchange'));
          break;
        }

        DisplayTask(subject);
        break;

    case "Calendar":
      loadCalendar();
      break;

    case "FilterNotes":
      await LoadPage("FilterNotes");

      let plants = await ServerRequest("GetPlants", {});
      plants = await plants.json();
      const selector = document.getElementById("plant-select");
      plants.forEach(plant => {
        selector.innerHTML += `<option value="${plant.plant_id}">${plant.name}</option>\n`;
      });

      let notes = await ServerRequest("GetNotes", {});
      notes = await notes.json();

      document.getElementById("filter-notes-btn").addEventListener("click", async (event) => {
        event.preventDefault();
        let dateFrom = document.getElementById("date-from-input").value;
        let dateTo = document.getElementById("date-from-input").value;
        let selectedPlant = selector.value;

        const filters = {
          dateTo: dateTo,
          dateFrom: dateFrom,
          plant: selectedPlant
        };

        filteredNotes = notes.filter(note => {
          return (
            (filters.dateFrom === "" || new Date(note.date) >= filters.dateFrom) &&
            (filters.dateTo === "" || new Date(note.date) <= filters.dateTo) &&
            (filters.plant === "" || note.plant_id == filters.plant)
          );
        });

        // if (dateFrom == "") {
        //   dateFrom = "01/01/1970";
        // }

        // if (dateTo == "") {
        //   dateTo = "01/01/2100";
        // }
        // if (selectedPlant == "") {
        //   filteredNotes = notes.filter(note => new Date(note.date) >= new Date(dateFrom) && new Date(note.date) <= new Date(dateTo));
        // }
        // else {
        //   filteredNotes = notes.filter(note => new Date(note.date) >= new Date(dateFrom) && new Date(note.date) <= new Date(dateTo) && note.plant_id == selectedPlant)
        // }
        await LoadPage("Notes");
        loadNotes(filteredNotes);
        history.replaceState(null, '', location.pathname + location.search + "#Notes"); // Чтобы не вызывать hashchange
      });
      break;

      case "FilterTasks":
        await LoadPage("FilterTasks");

        let plants2 = await ServerRequest("GetPlants", {});
        plants2 = await plants2.json();
        const plantSelector = document.getElementById("plant-select");
        plants2.forEach(plant => {
          plantSelector.innerHTML += `<option value="${plant.plant_id}">${plant.name}</option>\n`;
        });

        let tasks = await ServerRequest("GetTasks", {});
        tasks = await tasks.json();

        let taskTypes = await ServerRequest("GetTaskTypes");
        taskTypes = await taskTypes.json();
        const taskTypeSelector = document.getElementById("task-type-select");
        taskTypes.forEach(type => {
          taskTypeSelector.innerHTML += `<option value="${type.task_type_id}">${type.task_type_description}</option>\n`;
        });

        const taskTypeMap = taskTypes.reduce((map, item) => {
          map[item.task_type_description] = item.task_type_id;
          return map;
        }, {});

        let taskFrequencies = await ServerRequest("GetRepeatTypes");
        taskFrequencies = await taskFrequencies.json();
        const frequencySelector1 = document.getElementById("frequency-select");
        taskFrequencies.forEach(frequency => {
          frequencySelector1.innerHTML += `<option value="${frequency.repeat_type_id}">${frequency.repeat_type_description}</option>\n`;
        });

        const taskFrequencyMap = taskFrequencies.reduce((map, item) => {
          map[item.repeat_type_description] = item.repeat_type_id;
          return map;
        }, {});


        document.getElementById("filter-tasks-btn").addEventListener("click", async (event) => {
          event.preventDefault();
          let taskType = taskTypeSelector.value;
          let taskFrequency = frequencySelector1.value;
          let selectedPlant = plantSelector.value;

          const filters = {
            type: taskType,
            frequency: taskFrequency,
            plant: selectedPlant
          };

          filteredTasks = tasks.filter(task => {
            console.log(taskFrequencyMap[task.repeating] === filters.frequency, taskFrequencyMap[task.repeating], filters.frequency);
            return (
              (filters.type === "" || String(taskTypeMap[task.task_type]) === String(filters.type)) &&
              (filters.frequency === "" || String(taskFrequencyMap[task.repeating]) === String(filters.frequency)) &&
              (filters.plant === "" || task.plant_id == filters.plant)
            );
          });
          await LoadPage("Tasks");
          console.log(filteredTasks);
          loadTasks(filteredTasks);
          history.replaceState(null, '', location.pathname + location.search + "#Tasks"); // Чтобы не вызывать hashchange
        });
        break;
    }
  });

  window.dispatchEvent(new HashChangeEvent('hashchange'));
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
        //window.dispatchEvent(new HashChangeEvent('hashchange'));
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

async function loadPhotos(photoData) {
    const container = document.querySelector('.photos-container');

    try {
        container.innerHTML = '';
        photoData.forEach(photo => {
            const card = document.createElement('div');
            card.classList.add('photo-card');

            const img = document.createElement('img');
            img.src = `data:image/jpeg;base64,${photo.image}`;
            img.alt = 'Plant photo';

            img.addEventListener("click", () => {
              window.location.hash = `#Photo/${photo.photo_id}`;
              //window.dispatchEvent(new HashChangeEvent('hashchange'));
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
        //window.dispatchEvent(new HashChangeEvent('hashchange'));
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

async function loadNotes(notes) {
    const container = document.querySelector('.notes-container');
    container.innerHTML = '';

    try {
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
              //window.dispatchEvent(new HashChangeEvent('hashchange'));
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

  let plants = await ServerRequest("GetPlants", {});
  plants = await plants.json();
  const selector = document.getElementById("plant-select");
  plants.forEach(plant => {
    selector.innerHTML += `<option value="${plant.plant_id}">${plant.name}</option>\n`;
  });
  selector.value = noteInfo.plant_id;

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
      "plant_id": selector.value
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

  document.getElementById("delete-note-btn").addEventListener("click", async () => {
    let resp = await ServerRequest("DeleteNote", {"note_id": note_id});
    if (resp.status != 200) {
      alert(`ERROR:  ${resp.status}`);
    }
    else {
      window.location.hash = "#Notes";
    }
  });
}


async function loadTasks(tasks) {
    await LoadPage("Tasks");
    const container = document.querySelector('.tasks-container');

    // Очистка контейнера
    container.innerHTML = '';

    try {
        if (tasks.length === 0) {
            container.innerHTML = '<p>Нет доступных задач</p>';
            return;
        }

        tasks.forEach(task => {
            let desc = task.task_description.length > 70
                ? task.task_description.substring(0, 70) + "..."
                : task.task_description;

            const card = document.createElement('div');
            card.className = 'task-card';
            card.dataset.taskId = task.task_id; // Добавляем ID задачи

            const taskContent = document.createElement('div');
            taskContent.className = 'task-content';

            const title = document.createElement('h3');
            title.className = 'task-title';
            title.textContent = task.task_name;

            const description = document.createElement('p');
            description.className = 'task-description';
            description.textContent = desc;

            const type = document.createElement('p');
            type.className = 'task-type';
            type.textContent = task.task_type;

            const frequency = document.createElement('p');
            frequency.className = 'task-frequency';
            frequency.textContent = `Frequency: ${task.repeating}`;

            taskContent.appendChild(title);
            taskContent.appendChild(description);
            taskContent.appendChild(type);
            taskContent.appendChild(frequency);

            card.appendChild(taskContent);
            container.appendChild(card);
        });

        // Делегирование событий
        container.addEventListener("click", (event) => {
            const card = event.target.closest('.task-card');
            if (card) {
                const taskId = card.dataset.taskId;
                if (taskId) {
                    window.location.hash = `#Task/${taskId}`;
                }
            }
        });

    } catch (error) {
        console.error('Ошибка при загрузке задач:', error);
        container.innerHTML = '<p>Не удалось загрузить задачи. Попробуйте позже.</p>';
    }
}


async function DisplayTask(task_id) {
  await LoadPage("Task");

  plants = await ServerRequest("GetPlants", {});
  plants = await plants.json();
  selector = document.getElementById("plant-select");
  plants.forEach(plant => {
    selector.innerHTML += `<option value="${plant.plant_id}">${plant.name}</option>\n`;
  });

  let taskInfo = await ServerRequest("Task", {"task_id": task_id});
  taskInfo = await taskInfo.json();

  selector.value = taskInfo.plant_id;
  const nameInput = document.getElementById("task-name");
  const descriptionInput = document.getElementById("task-description");
  const dateInput = document.getElementById("task-date");
  const typeSelector = document.getElementById("task-type");
  const frequencySelector = document.getElementById("task-frequency");

  let resp = await ServerRequest("GetTaskTypes", {});
  taskTypes = await resp.json()
  resp = await ServerRequest("GetRepeatTypes", {});
  repeatTypes = await resp.json();

  typeSelector.innerHTML = '';
  taskTypes.forEach(type => {
    typeSelector.innerHTML += `<option value="${type.task_type_id}">${type.task_type_description}</option>\n`;
  });
  typeSelector.value = taskInfo.task_type_id;

  frequencySelector.innerHTML = '';
  repeatTypes.forEach(type => {
    frequencySelector.innerHTML += `<option value="${type.repeat_type_id}">${type.repeat_type_description}</option>\n`;
  });
  frequencySelector.value = taskInfo.repeat_type_id;


  nameInput.value = taskInfo.task_name;
  descriptionInput.value = taskInfo.task_description;
  dateInput.value = formatDateForInput(taskInfo.task_date);
  

  async function saveTaskHandler() {
    if (
      document.getElementById("task-name").value == "" ||
      document.getElementById("task-description").value == ""
    ) {
      alert("ЗАПОЛНИТЕ ВСЕ ПОЛЯ");
      return;
    }

    const response = await ServerRequest("UpdateTask", {
      "task_id": task_id,
      "plant_id": selector.value,
      "task_name": document.getElementById("task-name").value,
      "task_description": document.getElementById("task-description").value,
      "task_date":  document.getElementById("task-date").value,
      "task_type_id": typeSelector.value,
      "repeat_type_id": frequencySelector.value
    });

    if (response.status === 200) {
      return;
    } else {
      alert(`ERROR: ${response.status}`);
    }
  }

  function GoToPlant() {
    window.location.hash = `#Plant/${taskInfo.plant_id}`;
    //window.dispatchEvent(new HashChangeEvent('hashchange'));
  }

  const saveBtn = document.getElementById("save-task-btn");
  saveBtn.removeEventListener("click", saveTaskHandler);
  saveBtn.addEventListener("click", saveTaskHandler);

  const toPlantBtn = document.getElementById("plant-btn");
  toPlantBtn.removeEventListener("click", GoToPlant);
  toPlantBtn.addEventListener("click", GoToPlant);

  document.getElementById("delete-task-btn").addEventListener("click", async () => {
    let resp = await ServerRequest("DeleteTask", {"task_id": task_id});
    if (resp.status != 200) {
      alert(`ERROR:  ${resp.status}`);
    }
    else {
      window.location.hash = "#Tasks";
    }
  });
}

async function loadCalendar() {
  await LoadPage("Calendar");
  const monthYear = document.getElementById("month-year");
  const datesContainer = document.getElementById("dates");
  const prevBtn = document.getElementById("prev");
  const nextBtn = document.getElementById("next");

  let currentDate = new Date();

  async function renderCalendar(date) {
    let monthTasks = await ServerRequest("GetMonthTasks", {"date": date});
    monthTasks = await monthTasks.json();
    monthTasks = monthTasks["tasks"];
    let daysWithTasks = new Set();
    monthTasks.forEach(task => {
      daysWithTasks.add(task.task_day);
    });

    const year = date.getFullYear();
    const month = date.getMonth();

    // Название месяца и года
    const monthNames = [
      "Январь", "Февраль", "Март", "Апрель",
      "Май", "Июнь", "Июль", "Август",
      "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
    ];
    monthYear.textContent = `${monthNames[month]} ${year}`;

    // Первый день месяца (0 - воскресенье)
    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();

    // Очистка предыдущих дат
    datesContainer.innerHTML = "";

    // Добавление пустых ячеек перед первым днём
    for (let i = 0; i < (firstDay === 0 ? 6 : firstDay - 1); i++) {
      const emptyCell = document.createElement("div");
      datesContainer.appendChild(emptyCell);
    }

    // Добавление дней
    for (let day = 1; day <= daysInMonth; day++) {
      const dateCell = document.createElement("div");
      dateCell.textContent = day;
      dateCell.dataset.date = `${year}-${month + 1}-${day}`;

      // Выделение сегодняшнего дня
      const today = new Date();

      if (daysWithTasks.has(day)) {
        dateCell.classList.add("day-with-tasks");
      }

      if (
        day === today.getDate() &&
        month === today.getMonth() &&
        year === today.getFullYear()
      ) {
        dateCell.classList.remove("day-with-tasks");
        dateCell.classList.add("today");
        
        document.querySelectorAll(".calendar-dates div").forEach((div) => {
          div.classList.remove("selected-day");
        });
        dateCell.classList.add("selected-day");
        await ShowEvents(dateCell.dataset.date);
      }

      datesContainer.appendChild(dateCell);
    }
  }

  // Обработчики событий
  prevBtn.addEventListener("click", () => {
    const taskList = document.getElementById("tasks-list");
    taskList.innerHTML = '';
    currentDate.setMonth(currentDate.getMonth() - 1);
    renderCalendar(currentDate);
  });

  nextBtn.addEventListener("click", () => {
    const taskList = document.getElementById("tasks-list");
    taskList.innerHTML = '';
    currentDate.setMonth(currentDate.getMonth() + 1);
    renderCalendar(currentDate);
  });

  datesContainer.addEventListener("click", async (event) => {
    const target = event.target;

    if (target.tagName === "DIV" && target.dataset.date) {
      const selectedDate = target.dataset.date;

      // Можно выделить выбранный день
      document.querySelectorAll(".calendar-dates div").forEach((div) => {
        div.classList.remove("selected-day");
      });
      target.classList.add("selected-day");

      await ShowEvents(selectedDate);
    }
  });

  // Инициализация
  renderCalendar(currentDate);
}

async function ShowEvents(date) {
  const taskList = document.getElementById("tasks-list");
  taskList.innerHTML = '';
  let resp = await ServerRequest("GetDateTasks", {"date": date});
  if (resp.status != 200) {
    alert(`ERROR: ${resp.status}`);
    return;
  }
  resp = await resp.json();
  let tasks = resp["tasks"];
  tasks.forEach(task => {
        const taskDiv = document.createElement("div");
        taskDiv.className = "task-item";
        taskDiv.onclick = () => {
          window.location.hash = `#Task/${task.task_id}`;
          //window.dispatchEvent(new HashChangeEvent('hashchange'));
        }

        taskDiv.innerHTML = `
            <div class="task-title">${task.task_name}</div>
            <div class="task-type">Тип: ${task.task_type}</div>
        `;

        taskList.appendChild(taskDiv);
  });
}


