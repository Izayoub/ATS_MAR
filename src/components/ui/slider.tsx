import React, { forwardRef } from 'react'
import { cn } from '../../lib/utils'

export interface SliderProps {
  value?: number[]
  defaultValue?: number[]
  onValueChange?: (value: number[]) => void
  onValueCommit?: (value: number[]) => void
  min?: number
  max?: number
  step?: number
  orientation?: 'horizontal' | 'vertical'
  disabled?: boolean
  className?: string
  thumbClassName?: string
  trackClassName?: string
  rangeClassName?: string
}

const Slider = forwardRef<HTMLDivElement, SliderProps>(
  (
    {
      value,
      defaultValue,
      onValueChange,
      onValueCommit,
      min = 0,
      max = 100,
      step = 1,
      orientation = 'horizontal',
      disabled = false,
      className,
      thumbClassName,
      trackClassName,
      rangeClassName,
      ...props
    },
    ref
  ) => {
    const [internalValue, setInternalValue] = React.useState<number[]>(
      value || defaultValue || [min]
    )
    const [isDragging, setIsDragging] = React.useState(false)
    const sliderRef = React.useRef<HTMLDivElement>(null)

    // Utiliser la valeur contrôlée si fournie, sinon la valeur interne
    const currentValue = value || internalValue
    const currentValueNormalized = currentValue[0]

    // Calculer le pourcentage de la valeur
    const percentage = ((currentValueNormalized - min) / (max - min)) * 100

    // Gérer les changements de valeur
    const handleValueChange = React.useCallback(
      (newValue: number[]) => {
        if (!value) {
          setInternalValue(newValue)
        }
        onValueChange?.(newValue)
      },
      [value, onValueChange]
    )

    // Calculer la nouvelle valeur basée sur la position de la souris
    const calculateValueFromPosition = (clientX: number, clientY: number) => {
      if (!sliderRef.current) return currentValueNormalized

      const rect = sliderRef.current.getBoundingClientRect()
      
      let percentage: number
      if (orientation === 'horizontal') {
        percentage = (clientX - rect.left) / rect.width
      } else {
        percentage = 1 - (clientY - rect.top) / rect.height
      }

      percentage = Math.max(0, Math.min(1, percentage))
      const rawValue = min + percentage * (max - min)
      
      // Arrondir à l'étape la plus proche
      const steppedValue = Math.round(rawValue / step) * step
      return Math.max(min, Math.min(max, steppedValue))
    }

    // Gestionnaire de clic sur la piste
    const handleTrackClick = (event: React.MouseEvent) => {
      if (disabled) return

      event.preventDefault()
      const newValue = calculateValueFromPosition(event.clientX, event.clientY)
      handleValueChange([newValue])
      onValueCommit?.([newValue])
    }

    // Gestionnaire de début de glissement
    const handleThumbMouseDown = (event: React.MouseEvent) => {
      if (disabled) return

      event.preventDefault()
      setIsDragging(true)
      
      const handleMouseMove = (event: MouseEvent) => {
        const newValue = calculateValueFromPosition(event.clientX, event.clientY)
        handleValueChange([newValue])
      }

      const handleMouseUp = () => {
        setIsDragging(false)
        onValueCommit?.(currentValue)
        document.removeEventListener('mousemove', handleMouseMove)
        document.removeEventListener('mouseup', handleMouseUp)
      }

      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
    }

    // Gestionnaire de clavier
    const handleKeyDown = (event: React.KeyboardEvent) => {
      if (disabled) return

      let newValue = currentValueNormalized
      
      switch (event.key) {
        case 'ArrowRight':
        case 'ArrowUp':
          event.preventDefault()
          newValue = Math.min(max, currentValueNormalized + step)
          break
        case 'ArrowLeft':
        case 'ArrowDown':
          event.preventDefault()
          newValue = Math.max(min, currentValueNormalized - step)
          break
        case 'Home':
          event.preventDefault()
          newValue = min
          break
        case 'End':
          event.preventDefault()
          newValue = max
          break
        case 'PageUp':
          event.preventDefault()
          newValue = Math.min(max, currentValueNormalized + step * 10)
          break
        case 'PageDown':
          event.preventDefault()
          newValue = Math.max(min, currentValueNormalized - step * 10)
          break
        default:
          return
      }

      handleValueChange([newValue])
      onValueCommit?.([newValue])
    }

    return (
      <div
        ref={ref}
        className={cn(
          'relative flex w-full touch-none select-none items-center',
          orientation === 'vertical' && 'h-full w-4 flex-col',
          disabled && 'opacity-50 cursor-not-allowed',
          className
        )}
        {...props}
      >
        {/* Track */}
        <div
          ref={sliderRef}
          onClick={handleTrackClick}
          className={cn(
            'relative grow rounded-full bg-slate-200 dark:bg-slate-800',
            orientation === 'horizontal' ? 'h-2 w-full' : 'h-full w-2',
            !disabled && 'cursor-pointer',
            trackClassName
          )}
        >
          {/* Range */}
          <div
            className={cn(
              'absolute rounded-full bg-slate-900 dark:bg-slate-50',
              orientation === 'horizontal'
                ? 'h-full'
                : 'w-full',
              rangeClassName
            )}
            style={{
              [orientation === 'horizontal' ? 'width' : 'height']: `${percentage}%`,
              [orientation === 'horizontal' ? 'left' : 'bottom']: 0,
            }}
          />

          {/* Thumb */}
          <div
            className={cn(
              'absolute block rounded-full border-2 border-slate-900 bg-white shadow transition-colors',
              'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-950 focus-visible:ring-offset-2',
              'disabled:pointer-events-none disabled:opacity-50',
              'dark:border-slate-50 dark:bg-slate-950 dark:focus-visible:ring-slate-300',
              orientation === 'horizontal'
                ? 'h-5 w-5 top-1/2 -translate-y-1/2 -translate-x-1/2'
                : 'h-5 w-5 left-1/2 -translate-x-1/2 -translate-y-1/2',
              !disabled && 'hover:scale-110 cursor-grab',
              isDragging && !disabled && 'cursor-grabbing scale-110',
              thumbClassName
            )}
            style={{
              [orientation === 'horizontal' ? 'left' : 'bottom']: `${percentage}%`,
            }}
            onMouseDown={handleThumbMouseDown}
            onKeyDown={handleKeyDown}
            tabIndex={disabled ? -1 : 0}
            role="slider"
            aria-valuemin={min}
            aria-valuemax={max}
            aria-valuenow={currentValueNormalized}
            aria-orientation={orientation}
            aria-disabled={disabled}
          />
        </div>
      </div>
    )
  }
)

Slider.displayName = 'Slider'

export { Slider }