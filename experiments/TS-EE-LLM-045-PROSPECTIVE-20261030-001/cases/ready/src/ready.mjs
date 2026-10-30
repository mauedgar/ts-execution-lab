function isPlainObject(value) {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) {
    return false;
  }
  const proto = Object.getPrototypeOf(value);
  return proto === Object.prototype || proto === null;
}

function isNonEmptyString(value) {
  return typeof value === 'string' && value.length > 0;
}

export function selectReady(tasks, completed) {
  if (!Array.isArray(tasks)) {
    throw new TypeError('tasks must be an array');
  }
  if (!Array.isArray(completed)) {
    throw new TypeError('completed must be an array');
  }

  // Validate every task; keep an id -> deps map without mutating inputs.
  const tasksById = new Map();
  for (const task of tasks) {
    if (!isPlainObject(task)) {
      throw new TypeError('each task must be a plain object');
    }
    const id = task.id;
    const deps = task.deps;
    if (!isNonEmptyString(id)) {
      throw new TypeError('task id must be a nonempty string');
    }
    if (!Array.isArray(deps)) {
      throw new TypeError('task deps must be an array');
    }
    if (tasksById.has(id)) {
      throw new RangeError(`duplicate task id: ${id}`);
    }
    const seenDeps = new Set();
    const normalizedDeps = [];
    for (const dep of deps) {
      if (!isNonEmptyString(dep)) {
        throw new TypeError('each dependency must be a nonempty string');
      }
      if (seenDeps.has(dep)) {
        throw new RangeError(`duplicate dependency "${dep}" for task "${id}"`);
      }
      seenDeps.add(dep);
      normalizedDeps.push(dep);
    }
    tasksById.set(id, normalizedDeps);
  }

  // Every referenced dependency must exist; no self-dependencies.
  for (const [id, deps] of tasksById) {
    for (const dep of deps) {
      if (dep === id) {
        throw new RangeError(`task "${id}" depends on itself`);
      }
      if (!tasksById.has(dep)) {
        throw new RangeError(`task "${id}" references unknown dependency "${dep}"`);
      }
    }
  }

  // Completed IDs: nonempty strings, unique, and known tasks.
  const completedSet = new Set();
  for (const id of completed) {
    if (!isNonEmptyString(id)) {
      throw new TypeError('each completed id must be a nonempty string');
    }
    if (completedSet.has(id)) {
      throw new RangeError(`duplicate completed id: ${id}`);
    }
    if (!tasksById.has(id)) {
      throw new RangeError(`unknown completed id: ${id}`);
    }
    completedSet.add(id);
  }

  // Cycle detection over the entire graph, including completed nodes (Kahn).
  const indegree = new Map();
  const dependents = new Map();
  for (const [id, deps] of tasksById) {
    indegree.set(id, deps.length);
    for (const dep of deps) {
      let bucket = dependents.get(dep);
      if (bucket === undefined) {
        bucket = [];
        dependents.set(dep, bucket);
      }
      bucket.push(id);
    }
  }
  let remaining = tasksById.size;
  const queue = [];
  for (const [id, degree] of indegree) {
    if (degree === 0) {
      queue.push(id);
    }
  }
  while (queue.length > 0) {
    const current = queue.pop();
    remaining -= 1;
    const bucket = dependents.get(current);
    if (bucket !== undefined) {
      for (const next of bucket) {
        const nextDegree = indegree.get(next) - 1;
        indegree.set(next, nextDegree);
        if (nextDegree === 0) {
          queue.push(next);
        }
      }
    }
  }
  if (remaining !== 0) {
    throw new RangeError('dependency graph contains a cycle');
  }

  // Unfinished tasks whose every dependency is completed, default-sorted.
  const ready = [];
  for (const [id, deps] of tasksById) {
    if (completedSet.has(id)) {
      continue;
    }
    let allCompleted = true;
    for (const dep of deps) {
      if (!completedSet.has(dep)) {
        allCompleted = false;
        break;
      }
    }
    if (allCompleted) {
      ready.push(id);
    }
  }
  return ready.sort();
}
