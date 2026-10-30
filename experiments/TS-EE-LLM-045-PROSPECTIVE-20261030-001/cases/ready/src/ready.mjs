function isPlainObject(value) {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) {
    return false;
  }
  const proto = Object.getPrototypeOf(value);
  return proto === Object.prototype || proto === null;
}

export function selectReady(tasks, completed) {
  if (!Array.isArray(tasks)) {
    throw new TypeError('tasks must be an array');
  }
  if (!Array.isArray(completed)) {
    throw new TypeError('completed must be an array');
  }

  const depsById = new Map();
  const ids = [];

  for (const task of tasks) {
    if (!isPlainObject(task)) {
      throw new TypeError('each task must be a plain object');
    }

    const { id, deps } = task;
    if (typeof id !== 'string' || id.length === 0) {
      throw new TypeError('task id must be a non-empty string');
    }
    if (!Array.isArray(deps)) {
      throw new TypeError('task deps must be an array');
    }
    if (depsById.has(id)) {
      throw new RangeError('duplicate task id');
    }

    const seen = new Set();
    for (const dep of deps) {
      if (typeof dep !== 'string' || dep.length === 0) {
        throw new TypeError('dependency must be a non-empty string');
      }
      if (dep === id) {
        throw new RangeError('self-dependency');
      }
      if (seen.has(dep)) {
        throw new RangeError('duplicate dependency');
      }
      seen.add(dep);
    }

    depsById.set(id, deps.slice());
    ids.push(id);
  }

  const completedSet = new Set();
  for (const id of completed) {
    if (typeof id !== 'string' || id.length === 0) {
      throw new TypeError('completed id must be a non-empty string');
    }
    if (completedSet.has(id)) {
      throw new RangeError('duplicate completed id');
    }
    if (!depsById.has(id)) {
      throw new RangeError('unknown completed id');
    }
    completedSet.add(id);
  }

  for (const deps of depsById.values()) {
    for (const dep of deps) {
      if (!depsById.has(dep)) {
        throw new RangeError('unknown dependency');
      }
    }
  }

  const dependents = new Map();
  for (const id of ids) {
    dependents.set(id, []);
  }
  for (const [id, deps] of depsById) {
    for (const dep of deps) {
      dependents.get(dep).push(id);
    }
  }

  const remaining = new Map();
  for (const [id, deps] of depsById) {
    remaining.set(id, deps.length);
  }

  const queue = [];
  for (const id of ids) {
    if (remaining.get(id) === 0) {
      queue.push(id);
    }
  }

  let processed = 0;
  for (let i = 0; i < queue.length; i += 1) {
    const id = queue[i];
    processed += 1;
    for (const dependent of dependents.get(id)) {
      const next = remaining.get(dependent) - 1;
      remaining.set(dependent, next);
      if (next === 0) {
        queue.push(dependent);
      }
    }
  }

  if (processed !== ids.length) {
    throw new RangeError('cycle detected');
  }

  const ready = [];
  for (const id of ids) {
    if (completedSet.has(id)) {
      continue;
    }
    const deps = depsById.get(id);
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

  ready.sort();
  return ready;
}
