"use client"

import * as React from "react"
import { ChevronDown } from "lucide-react"
import { cn } from "../../lib/utils"
import { useEffect, type RefObject } from "react"

// Context pour gérer l'état du dropdown
interface DropdownMenuContextType {
  open: boolean
  setOpen: (open: boolean) => void
  trigger: React.RefObject<HTMLButtonElement>
}
interface DropdownMenuProps {
  children: React.ReactNode;
  defaultOpen?: boolean;
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
}

const DropdownMenuContext = React.createContext<DropdownMenuContextType | undefined>(undefined)

const useDropdownMenu = () => {
  const context = React.useContext(DropdownMenuContext)
  if (!context) {
    throw new Error("useDropdownMenu must be used within a DropdownMenu")
  }
  return context
}

// Hook pour gérer les clics à l'extérieur
export function useClickOutside(
  ref: RefObject<HTMLElement>,
  handler: (event: MouseEvent | TouchEvent) => void
) {
  useEffect(() => {
    const listener = (event: MouseEvent | TouchEvent) => {
      const target = event.target as Node;
      if (!ref.current || ref.current.contains(target)) {
        return;
      }
      handler(event);
    };

    document.addEventListener('mousedown', listener);
    document.addEventListener('touchstart', listener);

    return () => {
      document.removeEventListener('mousedown', listener);
      document.removeEventListener('touchstart', listener);
    };
  }, [ref, handler]);
}

// Composant principal DropdownMenu
interface DropdownMenuProps {
  children: React.ReactNode
  defaultOpen?: boolean
  open?: boolean
  onOpenChange?: (open: boolean) => void
}

const DropdownMenu = React.forwardRef<HTMLDivElement, DropdownMenuProps>(
  ({ children, defaultOpen = false, open: controlledOpen, onOpenChange }, ref) => {
    const [internalOpen, setInternalOpen] = React.useState(defaultOpen)
    const triggerRef = React.useRef<HTMLButtonElement>(null)
    const contentRef = React.useRef<HTMLDivElement>(null)

    const open = controlledOpen !== undefined ? controlledOpen : internalOpen
    const setOpen = React.useCallback(
      (newOpen: boolean) => {
        if (controlledOpen === undefined) {
          setInternalOpen(newOpen)
        }
        onOpenChange?.(newOpen)
      },
      [controlledOpen, onOpenChange]
    )

    useClickOutside(contentRef as React.RefObject<HTMLElement>, () => setOpen(false))

    React.useEffect(() => {
      const handleKeyDown = (event: KeyboardEvent) => {
        if (event.key === "Escape" && open) {
          setOpen(false)
          triggerRef.current?.focus()
        }
      }

      document.addEventListener("keydown", handleKeyDown)
      return () => document.removeEventListener("keydown", handleKeyDown)
    }, [open, setOpen])

    const contextValue = React.useMemo(
      () => ({
        open,
        setOpen,
        trigger: triggerRef as RefObject<HTMLButtonElement>,
      }),
      [open, setOpen]
    )

    return (
      <DropdownMenuContext.Provider value={contextValue}>
        <div ref={ref} className="relative inline-block text-left">
          {children}
        </div>
      </DropdownMenuContext.Provider>
    );
  }
)
DropdownMenu.displayName = "DropdownMenu"

// DropdownMenuTrigger
interface DropdownMenuTriggerProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  asChild?: boolean
  children: React.ReactNode
}

const DropdownMenuTrigger = React.forwardRef<HTMLButtonElement, DropdownMenuTriggerProps>(
  ({ className, children, asChild = false, ...props }, ref) => {
    const { open, setOpen, trigger } = useDropdownMenu()

    const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
      event.preventDefault()
      setOpen(!open)
      props.onClick?.(event)
    }

    const handleKeyDown = (event: React.KeyboardEvent<HTMLButtonElement>) => {
      if (event.key === "ArrowDown" || event.key === "ArrowUp") {
        event.preventDefault()
        setOpen(true)
      }
      props.onKeyDown?.(event)
    }

    // Update the clone element props
    if (asChild && React.isValidElement(children)) {
      return React.cloneElement(children, {
        ...props,
        ref: (node: HTMLButtonElement | null) => {
          // Type guard for function ref
          if (typeof ref === 'function') {
            ref(node)
          } 
          // Type guard for object ref
          else if (ref && 'current' in ref) {
            (ref as React.MutableRefObject<HTMLButtonElement | null>).current = node
          }
          // Type guard for trigger ref
          if (trigger && 'current' in trigger) {
            (trigger as React.MutableRefObject<HTMLButtonElement | null>).current = node
          }
        },
        onClick: handleClick,
        onKeyDown: handleKeyDown,
        "aria-haspopup": "menu",
        "aria-expanded": open,
        "data-state": open ? "open" : "closed",
      } as React.ComponentPropsWithRef<'button'>) // Changed type assertion
    }

    return (
      <button
        ref={ref || trigger}
        className={cn(
          "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
          "disabled:opacity-50 disabled:pointer-events-none",
          "hover:bg-accent hover:text-accent-foreground",
          "h-10 px-4 py-2",
          className
        )}
        onClick={handleClick}
        onKeyDown={handleKeyDown}
        aria-haspopup="menu"
        aria-expanded={open}
        data-state={open ? "open" : "closed"}
        {...props}
      >
        {children}
      </button>
    )
  }
)
DropdownMenuTrigger.displayName = "DropdownMenuTrigger"

// DropdownMenuContent
interface DropdownMenuContentProps extends React.HTMLAttributes<HTMLDivElement> {
  align?: "start" | "center" | "end"
  side?: "top" | "right" | "bottom" | "left"
  sideOffset?: number
  alignOffset?: number
}

const DropdownMenuContent = React.forwardRef<HTMLDivElement, DropdownMenuContentProps>(
  (
    {
      className,
      align = "center",
      side = "bottom",
      sideOffset = 4,
      alignOffset = 0,
      children,
      ...props
    },
    ref
  ) => {
    const { open, setOpen } = useDropdownMenu()
    const [position, setPosition] = React.useState({ top: 0, left: 0 })
    const contentRef = React.useRef<HTMLDivElement>(null)
    const { trigger } = useDropdownMenu()

    React.useEffect(() => {
      if (open && trigger.current && contentRef.current) {
        const triggerRect = trigger.current.getBoundingClientRect()
        const contentRect = contentRef.current.getBoundingClientRect()
        const viewport = {
          width: window.innerWidth,
          height: window.innerHeight,
        }

        let top = 0
        let left = 0

        // Calcul de la position verticale
        if (side === "bottom") {
          top = triggerRect.bottom + sideOffset
        } else if (side === "top") {
          top = triggerRect.top - contentRect.height - sideOffset
        } else if (side === "right") {
          top = triggerRect.top + (triggerRect.height / 2) - (contentRect.height / 2)
        } else if (side === "left") {
          top = triggerRect.top + (triggerRect.height / 2) - (contentRect.height / 2)
        }

        // Calcul de la position horizontale
        if (side === "bottom" || side === "top") {
          if (align === "start") {
            left = triggerRect.left + alignOffset
          } else if (align === "end") {
            left = triggerRect.right - contentRect.width - alignOffset
          } else {
            left = triggerRect.left + (triggerRect.width / 2) - (contentRect.width / 2) + alignOffset
          }
        } else if (side === "right") {
          left = triggerRect.right + sideOffset
        } else if (side === "left") {
          left = triggerRect.left - contentRect.width - sideOffset
        }

        // Vérification des limites de la viewport
        if (left + contentRect.width > viewport.width) {
          left = viewport.width - contentRect.width - 8
        }
        if (left < 8) {
          left = 8
        }
        if (top + contentRect.height > viewport.height) {
          top = triggerRect.top - contentRect.height - sideOffset
        }
        if (top < 8) {
          top = triggerRect.bottom + sideOffset
        }

        setPosition({ top, left })
      }
    }, [open, side, align, sideOffset, alignOffset])

    if (!open) return null

    return (
      <>
        {/* Overlay pour capturer les clics */}
        <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
        
        <div
          ref={(node) => {
            contentRef.current = node
            if (typeof ref === "function") {
              ref(node)
            } else if (ref) {
              ref.current = node
            }
          }}
          className={cn(
            "fixed z-50 min-w-[8rem] overflow-hidden rounded-md border bg-popover p-1 text-popover-foreground shadow-md",
            "data-[state=open]:animate-in data-[state=open]:fade-in-0 data-[state=open]:zoom-in-95",
            "data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95",
            "bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700",
            className
          )}
          style={{
            top: `${position.top}px`,
            left: `${position.left}px`,
          }}
          data-state={open ? "open" : "closed"}
          role="menu"
          {...props}
        >
          {children}
        </div>
      </>
    )
  }
)
DropdownMenuContent.displayName = "DropdownMenuContent"

// DropdownMenuItem
interface DropdownMenuItemProps extends React.HTMLAttributes<HTMLDivElement> {
  disabled?: boolean
  asChild?: boolean
}

const DropdownMenuItem = React.forwardRef<HTMLDivElement, DropdownMenuItemProps>(
  ({ className, disabled = false, asChild = false, children, onClick, ...props }, ref) => {
    const { setOpen } = useDropdownMenu()

    const handleClick = (event: React.MouseEvent<HTMLDivElement>) => {
      if (disabled) {
        event.preventDefault()
        return
      }
      onClick?.(event)
      setOpen(false)
    }

    const handleKeyDown = (event: React.KeyboardEvent<HTMLDivElement>) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault()
        if (!disabled) {
          onClick?.(event as any)
          setOpen(false)
        }
      }
    }

    if (asChild && React.isValidElement(children)) {
      return React.cloneElement(children, {
        ...props,
        ref: (node: HTMLDivElement | null) => {
          if (typeof ref === 'function') {
            ref(node)
          } else if (ref && 'current' in ref) {
            (ref as React.MutableRefObject<HTMLDivElement | null>).current = node
          }
        },
        onClick: handleClick,
        onKeyDown: handleKeyDown,
        role: "menuitem",
        tabIndex: disabled ? -1 : 0,
        "data-disabled": disabled,
      } as React.ComponentPropsWithRef<'div'>) // Changed type assertion
    }

    return (
      <div
        ref={ref}
        className={cn(
          "relative flex cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors",
          "focus:bg-accent focus:text-accent-foreground",
          "data-[disabled]:pointer-events-none data-[disabled]:opacity-50",
          "hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer",
          disabled && "opacity-50 pointer-events-none",
          className
        )}
        role="menuitem"
        tabIndex={disabled ? -1 : 0}
        data-disabled={disabled}
        onClick={handleClick}
        onKeyDown={handleKeyDown}
        {...props}
      >
        {children}
      </div>
    )
  }
)
DropdownMenuItem.displayName = "DropdownMenuItem"

// DropdownMenuSeparator
interface DropdownMenuSeparatorProps extends React.HTMLAttributes<HTMLDivElement> {}

const DropdownMenuSeparator = React.forwardRef<HTMLDivElement, DropdownMenuSeparatorProps>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn("-mx-1 my-1 h-px bg-muted bg-gray-200 dark:bg-gray-600", className)}
      role="separator"
      {...props}
    />
  )
)
DropdownMenuSeparator.displayName = "DropdownMenuSeparator"

// DropdownMenuLabel
interface DropdownMenuLabelProps extends React.HTMLAttributes<HTMLDivElement> {
  inset?: boolean
}

const DropdownMenuLabel = React.forwardRef<HTMLDivElement, DropdownMenuLabelProps>(
  ({ className, inset, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        "px-2 py-1.5 text-sm font-semibold text-gray-900 dark:text-gray-100",
        inset && "pl-8",
        className
      )}
      {...props}
    />
  )
)
DropdownMenuLabel.displayName = "DropdownMenuLabel"

// DropdownMenuGroup
interface DropdownMenuGroupProps extends React.HTMLAttributes<HTMLDivElement> {}

const DropdownMenuGroup = React.forwardRef<HTMLDivElement, DropdownMenuGroupProps>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn("", className)} role="group" {...props} />
  )
)
DropdownMenuGroup.displayName = "DropdownMenuGroup"

// Export des composants
export {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuLabel,
  DropdownMenuGroup,
}


