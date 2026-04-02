// ============================================================
// MiroFish Router Type Definitions
// ============================================================

import type { RouteRecordRaw } from 'vue-router'
import type { NavigationGuardNext, RouteLocationNormalized } from 'vue-router'

// Re-export vue-router types for convenience
export { RouteRecordRaw }

export type NavigationGuard = (
  to: RouteLocationNormalized,
  from: RouteLocationNormalized,
  next: NavigationGuardNext
) => unknown

// Route record with component typed as a function component
export interface AppRouteRecordRaw extends Omit<RouteRecordRaw, 'component'> {
  component?: RouteRecordRaw['component']
  props?: RouteRecordRaw['props']
}
