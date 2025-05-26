document.addEventListener("DOMContentLoaded", async () => {
  window.dispatchEvent(new HashChangeEvent('hashchange'));
  // Добавить вход
});

window.addEventListener('hashchange', async () => {
  let action = window.location.hash.split('#')[1].split("?")[0];

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
      
  }
});

async function LoadPage(action) {
  let response = await ServerRequest("GetPage", {"Page": action});
  if (response.status == 200) {
    let html = await response.text();
    document.getElementById("content-block").innerHTML = html;
  }
  else {
    document.getElementById("content-block").innerHTML = "<h1>ERROR</h1>";
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
        displayPlantData(plant.name, plant.science_name, Math.round(plant.place), plant.main_photo);
      });
  });
}



