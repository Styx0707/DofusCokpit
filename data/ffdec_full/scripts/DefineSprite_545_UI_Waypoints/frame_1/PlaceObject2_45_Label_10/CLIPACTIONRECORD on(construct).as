on(construct){
   while(true)
   {
      if(!(0x2962A245 | 0x2962A245))
      {
         if(!ord("\x04"))
         {
            break;
         }
      }
      else
      {
         §§push(false);
      }
      if(!§§pop())
      {
         enabled = true;
         html = false;
         multiline = false;
         styleName = "WhiteCenterSmallLabel";
         §§push("text");
         §§push("Pays (Territoire)");
         if(!getTimer())
         {
            setProperty(§§pop(), _X, §§pop());
            §§goto(addr12f7f);
         }
      }
      set(§§pop(),§§pop());
      §§push("wordWrap");
      §§push(false);
      break;
   }
   set(§§pop(),§§pop());
   addr12f7f:
}
